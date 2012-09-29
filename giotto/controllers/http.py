import inspect
from werkzeug.wrappers import Request, Response
from giotto import controller_maps
from giotto.primitives import GiottoPrimitive
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

        model, view, controller = app.get_model_view_controller()

        import debug

        try:
            output = controller.get_response()
        except InvalidInput as exc:
            # the model failed because of invalid input.
            # render with view with the error data.
            output = controller.handle_error(exc)
        else:
            if hasattr(view, 'render'):
                # if the view has a render method, use that, otherwise render the view by
                # calling it
                content, mimetype = view.render(model)
            else:
                content = view(model(**controller_args))
                mimetype = "text/plain"

        ## do output middleware here

        wsgi_response = Response(content, mimetype=mimetype)
        return wsgi_response(environ, start_response)

    return application

def primitive_from_argspec(data, argspec):
    """
    Fill in primitives from the argspec
    """
    kwargs = dict(zip(*[reversed(l) for l in (argspec.args, argspec.defaults or [])]))
    args2 = [item for item in argspec.args if item not in kwargs.keys()]

    for item, value in kwargs.iteritems():
        if GiottoPrimitive in value.mro():
            kwargs[item] = get_primitive(request, value)

    for arg in args2:
        kwargs[arg] = request.args[arg]

    return kwargs


# stubs, replace with something better later
class User(object): pass
class AnonymousUser(object): pass

def get_primitive(request, primitive):
    """
    Exract a primitive from the request and return it.
    """
    if primitive.__name__ == "LOGGED_IN_USER":
        user = request.cookies.get('user')
        if user:
            return User()
        else:
            return AnonymousUser()
