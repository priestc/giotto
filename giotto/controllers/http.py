import urllib

from giotto.controllers import GiottoController
from werkzeug.wrappers import Request, Response
from giotto.utils import super_accept_to_mimetype
from giotto.exceptions import NoViewMethod

http_execution_snippet = """
mock = '--mock' in sys.argv
from werkzeug.serving import run_simple
from giotto.controllers.http import make_app
application = make_app(programs, model_mock=mock)
initialize_giotto(config)
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

    def get_mimetype(self):
        sa = self.get_super_accept()
        if sa:
            return sa
        accept = self.request.headers['Accept']
        has_json_in_view = hasattr(self.program.view, 'application_json')
        if accept == '*/*' and self.request.is_xhr and has_json_in_view:
            # return json on ajax calls if no accept headers are present.
            # only if the view has implemented a application/json method
            return "application/json"

        if accept != '*/*' and not accept.startswith('text/html'):
            return accept
        return self.default_mimetype

    def get_program_name(self):
        splitted = self.request.path[1:].split('.')
        return splitted[0]

    def get_super_accept(self):
        splitted = self.request.path[1:].split('.')
        if len(splitted) > 1:
            return super_accept_to_mimetype(splitted[1])

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
                'body': 'Unsupported Media Type: %s' % self.get_mimetype()
            }
        
        # convert to a format appropriate to the wsgi Response api.
        response = Response(
            status=code,
            response=result['body'],
            mimetype=result['mimetype'],
        )

        # now do middleware
        return self.execute_output_middleware_stream(response) 

    def get_primitive(self, primitive):
        if primitive == 'RAW_PAYLOAD':
            return self.get_data()
        if primitive == 'LOGGED_IN_USER':
            return self.request.user

def make_app(programs, model_mock=False, cache=None):
    
    def application(environ, start_response):
        """
        WSGI app for serving giotto applications
        """
        request = Request(environ)
        controller = HTTPController(request, programs, model_mock=model_mock, cache=cache)
        wsgi_response = controller.get_concrete_response()
        return wsgi_response(environ, start_response)

    return application

















