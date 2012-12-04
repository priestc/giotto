import urllib
import magic

from giotto.controllers import GiottoController
from werkzeug.wrappers import Request, Response
from giotto.exceptions import NoViewMethod

http_execution_snippet = """
mock = '--model-mock' in sys.argv
from werkzeug.serving import run_simple
from giotto.controllers.http import make_app
application = make_app(manifest, model_mock=mock)
if '--run' in sys.argv:
    run_simple('127.0.0.1', 5000, application, use_debugger=True, use_reloader=True)"""

class HTTPController(GiottoController):
    name = 'http'
    default_mimetype = 'text/html'

    def get_invocation(self, program, data, ext=""):
        if ext and not ext.startswith('.'):
            ext = '.%s' % ext

        if type(data) is list:
            params = "/".join(data)
        else:
            params = '?' + urllib.urlencode(data)
        return "%s%s%s" % (program, ext, params)

    def mimetype_override(self):
        accept = self.request.headers['Accept']
        has_json_in_view = hasattr(self.program.view, 'application_json')
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

    def get_data(self):
        data = {}
        if self.request.method == 'GET':
            data = self.request.args
        elif self.request.method == 'POST':
            data = self.request.form
        return data

    def get_concrete_response(self):
        code = 200
        try:
            result = self._get_generic_response_data()
        except NoViewMethod:
            code = 415
            result = {
                'mimetype': 'text/plain',
                'body': 'Unsupported Media Type: %s' % self.mimetype
            }
        
        body = result['body']
        if hasattr(body, 'close'):
            # response is a file, determine the mime of that file and return
            mime = magic.from_buffer(body.read(1024), mime=True)
            body.seek(0)
            response = Response(
                status=code,
                response=body,
                mimetype=mime
            )
        else:
            # convert to a format appropriate to the wsgi Response api.
            response = Response(
                status=code,
                response=body,
                mimetype=result['mimetype'],
            )

        # now do middleware
        return self.execute_output_middleware_stream(response)

    def get_primitive(self, primitive):
        if primitive == 'RAW_PAYLOAD':
            return self.get_data()
        if primitive == 'LOGGED_IN_USER':
            return self.request.user
        if primitive == 'ALL_PROGRAMS':
            return self.programs

def make_app(programs, model_mock=False, cache=None):
    
    def application(environ, start_response):
        """
        WSGI app for serving giotto applications
        """
        request = Request(environ)
        controller = HTTPController(request, programs, model_mock=model_mock)
        wsgi_response = controller.get_concrete_response()
        return wsgi_response(environ, start_response)

    return application

















