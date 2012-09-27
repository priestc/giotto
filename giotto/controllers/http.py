import inspect
from werkzeug.wrappers import Request, Response
from giotto import controller_maps
from giotto.primitives import GiottoPrimitive
from giotto.core import GiottoHttpException, config
from giotto.exceptions import InvalidInput

global config


def execute_controller(request, module, controller_maps):
    controller_name = module.__name__ + '.controllers.' + request.path[1:].replace('/', '.')
    ret = controller_maps['http'].get(controller_name, None)
    if not ret:
        raise GiottoHttpException('Can not find controller: %s in %s' % (controller_name, controller_maps))

    controller = ret['app']
    argspec = ret['argspec']
    controller_args = primitive_from_argspec(request, argspec)
    m, v = controller(**controller_args)
    return m, v, controller_args

def make_app(module):

    config = module.config
    
    def application(environ, start_response):
        """
        WSGI app for serving giotto applications
        """
        request = Request(environ)

        ## do input middleware here

        view, model_pair, controller_args = execute_controller(request, module, controller_maps)

        # if a model was attached to this controller, the controller will return
        # the model and controller as a tuple, otherwise if there is no model,
        # the the model_pair will be just the controller_args

        try:
            if type(model_pair) is tuple:
                model = model_pair[0](**model_pair[1])
            else:
                # no model, use a empty callable
                model = lambda: x
        except InvalidInput as exc:
            # the model failed because of invalid input.
            # render with view with the error data.
            import debug
            content, mimetype = view.render(None, errors=exc.errors, input=controller_args)
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

def primitive_from_argspec(request, argspec):
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
