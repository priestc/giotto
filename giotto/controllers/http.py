import traceback
import base64

try:
    from urllib.parse import urlencode, unquote
except ImportError:
    from urllib import urlencode, unquote

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from giotto.exceptions import NoViewMethod, InvalidInput, NotAuthorized, DataNotFound, ProgramNotFound
from giotto.controllers import GiottoController
from giotto.control import Redirection
from giotto.utils import render_error_page
from webob import Request, Response
from webob.exc import (
    HTTPUnsupportedMediaType, HTTPMethodNotAllowed, HTTPFound,
    HTTPNotFound, HTTPForbidden
)

http_execution_snippet = """import sys
mock = '--model-mock' in sys.argv
from giotto import get_config
from giotto.controllers.http import make_app, fancy_error_template_middleware, serve

application = make_app(manifest, model_mock=mock)

if not get_config('debug'):
    application = fancy_error_template_middleware(application)

if '--run' in sys.argv:
    serve('127.0.0.1', 5000, application, ssl=None, use_debugger=True, use_reloader=True)

if '--run-ssl' in sys.argv:
    serve('127.0.0.1', 443, application, ssl='adhoc', use_debugger=True, use_reloader=True)
"""


def serve(ip, port, application, ssl=None, processes=1, **kwargs):
    """
    Serve a wsgi app (any wsgi app) through with either werkzeug's runserver
    or the one that comes with python. Setting `processes` to anything other than 1
    will prevent the debigger from working.
    """

    try:
        # use werkzeug if its there
        from werkzeug.serving import run_simple
        print("Using Werkzeug run_simple")
        run_simple(ip, port, application, ssl_context=ssl, processes=processes, **kwargs)
        return
    except ImportError:
        pass

    # otherwise just use python's built in wsgi webserver
    from wsgiref.simple_server import make_server
    server = make_server(ip, port, application)
    print("Serving on %s:%s, using built in Python server" % (ip, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

def make_url(invocation, args=[], kwargs={}):
    """
    >>> make_url('some/path/program', ['arg1', 'arg2'], {'arg3': 4})
    '/some/path/program/arg1/arg2?arg3=4'
    """
    if not invocation.endswith('/'):
        invocation += '/'
    if not invocation.startswith('/'):
        invocation = '/' + invocation

    url = invocation

    for arg in args:
        url += str(arg) + "/"

    if kwargs:
        url = url[:-1]
        url += "?" + urlencode(kwargs)
    
    return url


class HTTPController(GiottoController):
    name = 'http'
    default_mimetype = 'text/html'

    def mimetype_override(self):
        accept = self.request.headers.get('Accept', '')
        has_json_in_view = self.program.view and self.program.view.can_render('json')
        if accept == '*/*' and self.request.is_xhr and has_json_in_view:
            # return json on ajax calls if no accept headers are present.
            # and only if the view has implemented a application/json method
            return "application/json"

        if accept != '*/*' and not accept.startswith('text/html'):
            return accept
        return None

    def get_invocation(self):
        return self.request.path

    def get_controller_name(self):
        return 'http-%s' % self.request.method.lower()

    def get_raw_data(self):
        data = {}
        if self.request.method == 'GET':
            data = self.request.GET
        elif self.request.method == 'POST':
            data = self.request.POST

        return data

    def get_concrete_response(self):
        try:
            result = self.get_data_response()
        except NoViewMethod as exc:
            return HTTPUnsupportedMediaType(
                body=render_error_page(415, exc, mimetype=self.mimetype),
                content_type="text/html"
            )
        except InvalidInput as exc:
            ## if the model raises a InvalidInput, retry the request as
            ## a GET request for the same program, and set the code to 400.
            request = make_duplicate_request(self.request)
            request.method = 'GET'
            c = HTTPController(request, self.manifest, self.model_mock, errors=exc)
            response = c.get_response()
            response.status_int = 400
            return response
        except NotAuthorized as exc:
            return HTTPForbidden(
                body=render_error_page(403, exc, mimetype=self.mimetype),
                content_type="text/html"
            )
        except (DataNotFound, ProgramNotFound) as exc:
            return HTTPNotFound(
                body=render_error_page(404, exc, mimetype=self.mimetype),
                content_type="text/html"
            )

        if type(result['body']) == Redirection:
            response = HTTPFound(location=result['body'].path)
        else:
            lazy = None
            body = result['body']

            if type(body) == tuple:
                lazy = body
                body = ''

            if hasattr(body, 'read'):
                body = body.read()

            response = Response(
                status=200,
                body=body,
                content_type=result['mimetype'],
            )

            response.lazy_data = lazy

        return response

    def persist(self, persist, response):
        for key, value in persist.items():
            response.set_cookie(key, value)
        return response

    def get_primitive(self, primitive):
        if primitive == 'USER':
            auth = self.request.authorization and self.request.authorization[1]
            userpass = (auth and base64.b64decode(auth)) or None
            return (userpass and userpass.split(":")[0]) or None
        if primitive == 'ALL_DATA':
            return self.get_raw_data()
        if primitive == 'LOGGED_IN_USER':
            return self.request.user
        if primitive == 'RAW_INVOCATION_ARGS':
            return unquote('/'.join(self.path_args))

        raise Exception("Primitive not supported")


def make_duplicate_request(request):
    """
    Since werkzeug request objects are immutable, this is needed to create an
    identical reuet object with immutable values so it can be retried after a
    POST failure.
    """
    class FakeRequest(object):
        method = 'GET'
        path = request.path
        headers = request.headers
        GET = request.GET
        POST = request.POST
        user = getattr(request, 'user', None)
        cookies = request.cookies
        is_xhr = request.is_xhr
    return FakeRequest()


def make_app(manifest, model_mock=False, cache=None):
    
    def application(environ, start_response):
        """
        WSGI app for serving giotto applications
        """
        request = Request(environ)
        controller = HTTPController(request, manifest, model_mock=model_mock)
        try:
            wsgi_response = controller.get_response()
        except:
            # TODO: switch to django
            #get_config('db_session').rollback()
            raise

        return wsgi_response(environ, start_response)

    return application


def fancy_error_template_middleware(app):
    """
    WGSI middleware for catching errors and rendering the error page.
    """
    def application(environ, start_response):
        try:
            return app(environ, start_response)
        except Exception as exc:
            sio = StringIO()
            traceback.print_exc(file=sio)
            sio.seek(0)
            response =  Response(
                status=500,
                body=render_error_page(500, exc, traceback=sio.read()),
                content_type="text/html"
            )
            return response(environ, start_response)

    return application





