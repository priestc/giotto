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
        
        response = Response(
                status=code,
                response=result['body'],
                mimetype=result['mimetype'],
            )

        # now do middleware
        return response

    def get_primitive(self, primitive):
        if primitive == 'RAW_PAYLOAD':
            return self.get_raw_data()
        if primitive == 'LOGGED_IN_USER':
            return self.request.user
        if primitive == 'ALL_PROGRAMS':
            return self.manifest.get_all_programs()

def make_app(programs, model_mock=False, cache=None):
    
    def application(environ, start_response):
        """
        WSGI app for serving giotto applications
        """
        request = Request(environ)
        controller = HTTPController(request, programs, model_mock=model_mock)
        wsgi_response = controller.get_response()
        return wsgi_response(environ, start_response)

    return application