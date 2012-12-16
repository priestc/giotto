import copy
import urllib

from giotto.exceptions import NoViewMethod, InvalidInput
from giotto.controllers import GiottoController
from giotto.control import Redirection
from werkzeug.wrappers import Request, Response
from werkzeug.utils import redirect


http_execution_snippet = """
mock = '--model-mock' in sys.argv
from werkzeug.serving import run_simple
from giotto.controllers.http import make_app
application = make_app(manifest, model_mock=mock)
if '--run' in sys.argv:
    run_simple('127.0.0.1', 5000, application, use_debugger=True, use_reloader=True)"""


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
        url += "?" + urllib.urlencode(kwargs)
    
    return url


class HTTPController(GiottoController):
    name = 'http'
    default_mimetype = 'text/html'

    def mimetype_override(self):
        accept = self.request.headers['Accept']
        has_json_in_view = any([x for x in self.program.view.render_map.keys() if 'json' in x])
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
            data = self.request.args
        elif self.request.method == 'POST':
            data = self.request.form
        return data

    def get_concrete_response(self):
        code = 200
        try:
            result = self.get_data_response()
        except NoViewMethod:
            code = 415
            result = {
                'mimetype': 'text/plain',
                'body': 'Unsupported Media Type: %s' % self.mimetype
            }
        except InvalidInput as exc:
            request = make_duplicate_request(self.request)
            request.method = 'GET'
            c = HTTPController(request, self.manifest, self.model_mock, errors=exc)
            response = c.get_response()
            response.status_code = 400
            return response

        if type(result) == Redirection:
            invocation, args, kwargs = result.rendered_invocation
            response = redirect(make_url(invocation, args, kwargs))
        else:
            response = Response(
                status=code,
                response=result['body'],
                mimetype=result['mimetype'],
            )

        return response

    def get_primitive(self, primitive):
        if primitive == 'RAW_PAYLOAD':
            return self.get_raw_data()
        if primitive == 'LOGGED_IN_USER':
            return self.request.user
        if primitive == 'ALL_PROGRAMS':
            return self.manifest.get_all_programs()


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
        args = request.args
        user = request.user
        cookies = request.cookies
        is_xhr = request.is_xhr
    return FakeRequest()