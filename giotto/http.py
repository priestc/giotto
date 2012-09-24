import inspect
from werkzeug.wrappers import Request, Response
from giotto import controller_maps
from giotto.primitives import GiottoPrimitive
from giotto.core import GiottoHttpException, User, AnonymousUser


def make_app(module):

    def application(environ, start_response):
        """
        WSGI app for serving giotto applications
        """
        request = Request(environ)
        controller_name = module.__name__ + '.controllers.' + request.path[1:].replace('/', '.')
        
        ret = controller_maps['http'].get(controller_name, None)

        if not ret:
            raise GiottoHttpException('Can not find controller: %s in %s' % (controller_name, controller_maps))

        controller = ret['app']
        argspec = ret['argspec']
        controller_args = primitive_from_argspec(request, argspec)
        html = controller(**controller_args)

        response = Response(html, mimetype='text/html')
        return response(environ, start_response)

    return  application

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
