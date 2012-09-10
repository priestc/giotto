from werkzeug.wrappers import Request, Response
from giotto import controller_maps
from giotto.primitives import GiottoPrimitive

class GiottoHttpException(Exception):
    pass

def make_app(module):
    
    def application(environ, start_response):
        """
        WSGI app for serving giotto applications
        """
        request = Request(environ)
        model_name = request.path[1:].replace('/', '.')
        
        ret = controller_maps['http'].get(model_name, None)

        if not ret:
            raise GiottoHttpException('Can not find model: %s' % model_name)

        model = ret['app']
        argspec = ret['argspec']

        model_args = primitive_from_argspec(request, argspec)
        html = model(**model_args)

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


class User(object): pass
class AnonymousUser(object): pass

def get_primitive(request, primitive):
    if primitive.__name__ == "LOGGED_IN_USER":
        user = request.cookies.get('user')
        if user:
            return User()
        else:
            return AnonymousUser()
