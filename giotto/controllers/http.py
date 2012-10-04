from werkzeug.wrappers import Request, Response
from giotto.core import GiottoHttpException, GiottoApp, config
from giotto.exceptions import InvalidInput

global config

class BaseHTTP(GiottoApp):
    def __init__(self, module, request):
        self.request = request
        self.module = module

    def get_controller_tip_path(self):
        """
        Return the full path of the controller tip,
        e.g. blog.controllers.create_blog
        """
        path = self.request.path
        return self.module.__name__ + '.controllers.' + path[1:].replace('/', '.')

    def get_view_args(self, model, controller_args):
        """
        Return the arguments that will go into the view.
        """
        return model(**controller_args)

class HttpGet(BaseHTTP):
    name = 'http-get'

    def data(self, arg):
        return self.request.args[arg]

    def get_primitive(self, name):
        if name == 'RAW_DATA':
            return self.request.args

    def handle_error(self, exc):
        previous_program = self.request.referrer
        previous_error = exc.errors
        previous_input = self.controller_args


class HttpPost(BaseHTTP):
    name = 'http-post'

    def data(self, arg):
        return self.request.form[arg]

    def get_primitive(self, name):
        if name == 'RAW_DATA':
            return self.request.form

def make_app(module):

    config = module.config
    
    def application(environ, start_response):
        """
        WSGI app for serving giotto applications
        """
        request = Request(environ)

        ## do input middleware here

        if request.method == "POST":
            app = HttpPost(module, request)
        elif request.method == 'GET':
            app = HttpGet(module, request)

        try:
            output = app.get_response()
        except InvalidInput as exc:
            # the model failed because of invalid input.
            # render with view with the error data.
            output = app.handle_error(exc)

        ## do output middleware here

        if type(output) is not dict:
            res = {
                'mimetype': "text/plain",
                'status': 200,
                'response': output,
            }
        else:
            res = output

        wsgi_response = Response(**res)
        return wsgi_response(environ, start_response)

    return application

















