import traceback

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

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
    HTTPUnsupportedMediaType, HTTPMethodNotAllowed, HTTPTemporaryRedirect,
    HTTPNotFound, HTTPForbidden
)

http_execution_snippet = """
mock = '--model-mock' in sys.argv
from giotto.controllers.http import make_app, error_handler, serve

application = make_app(manifest, model_mock=mock)

if not config.debug:
    application = error_handler(application)

if '--run' in sys.argv:
    serve('127.0.0.1', 5000, application, use_debugger=True, use_reloader=True)"""


def serve(ip, port, application, **kwargs):
    """
    Serve a wsgi app (any wsgi app) through with either werkzeug's runserver
    or the one that comes with python.
    """
    try:
        from werkzeug.serving import run_simple
        run_simple(ip, port, application, **kwargs)
        return
    except ImportError:
        pass

    from wsgiref.simple_server import make_server
    server = make_server(ip, port, application)
    print("Serving on %s:%s" % (ip, port))
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
        has_json_in_view = self.program.view.can_render('json')
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
                body=render_error_page(415, exc),
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
                body=render_error_page(403, exc),
                content_type="text/html"
            )
        except (DataNotFound, ProgramNotFound) as exc:
            return HTTPNotFound(
                body=render_error_page(404, exc),
                content_type="text/html"
            )

        if type(result['body']) == Redirection:
            response = HTTPTemporaryRedirect(location=result['body'].path)
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
        if primitive == 'ALL_DATA':
            return self.get_raw_data()
        if primitive == 'LOGGED_IN_USER':
            return self.request.user
        if primitive == 'ALL_PROGRAMS':
            return self.manifest.get_all_programs()


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
        wsgi_response = controller.get_response()
        return wsgi_response(environ, start_response)

    return application


def error_handler(app):
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
                body=render_error_page(500, exc, sio.read()),
                content_type="text/html"
            )
            return response(environ, start_response)

    return application





