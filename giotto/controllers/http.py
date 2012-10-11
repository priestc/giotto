from giotto.controllers import GiottoController
from werkzeug.wrappers import Request, Response

http_execution_snippet = """
if controller == 'http-dev':
    from werkzeug.serving import run_simple
    from giotto.controllers.http import make_app
    app = make_app(programs)
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
"""

class HTTPController(GiottoController):
    name = 'http'
    default_mimetype = 'text/html'

    def get_mimetype(self):
        accept = self.request.headers['Accept']
        has_json_in_view = hasattr(self.program.view[0], 'application_json')
        if accept == '*/*' and self.request.is_xhr and has_json_in_view:
            # return json on ajax calls if no accept headers are present.
            # only if the view has implemented a application/json method
            return "application/json"
        if accept != '*/*' and not accept.startswith('text/html'):
            return accept
        return self.default_mimetype

    def get_program_name(self):
        return self.request.path[1:].replace('/', '.')

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
        result = self._get_generic_response_data()
        # convert to a format appropriate to the wsgi Response api.
        response = Response(
            response=result['body'],
            mimetype=result['mimetype'],
        )

        # now do middleware
        return self.execute_output_middleware_stream(response) 

    def get_primitive(self, primitive):
        if primitive == 'RAW_PAYLOAD':
            return self.get_data()

def make_app(programs):
    
    def application(environ, start_response):
        """
        WSGI app for serving giotto applications
        """
        request = Request(environ)
        controller = HTTPController(request, programs)
        wsgi_response = controller.get_concrete_response()
        return wsgi_response(environ, start_response)

    return application

















