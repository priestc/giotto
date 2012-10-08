from functools import wraps
from collections import defaultdict
import inspect

import decorator

from giotto.primitives import GiottoPrimitive

# where all apps are stored
app_map = defaultdict(lambda: {})

# the config file of the project that giotto is handling
config = None

class GiottoHttpException(Exception):
    pass

def execute_input_middleware_stream(controller, stream):
    def get(item):
        pass
    classes = [get(item) for item in stream]

class GiottoApp(object):
    """
    Base class for all Giotto application controllers.
    """

    def get_controller_tip_path(self):
        raise NotImplementedError

    def get_model_view_controller(self):
        """
        Calculate the controller tip, then return the model, view, and controller
        along with the primitives filled in.
        """
        ctp = self.get_controller_tip_path()
        ret = app_map[self.name][ctp]

        controller_args = self.get_controller_args(ret['argspec'])
        view, (model, _) = ret['app'](**controller_args)

        return model, view, controller_args

    def get_controller_args(self, argspec):
        """
        Given an argspec, return the controller args filled in with data from the
        invocation.
        """
        # dict of args that were defined in the controller tip with defaults
        # can be primitives, can be constants...
        kwargs = dict(zip(*[reversed(l) for l in (argspec.args, argspec.defaults or [])]))

        # list of args that do not contain primitives, these need to be replaced
        # data from the request.form / request.args / command line args / etc.
        args = [item for item in argspec.args if item not in kwargs.keys()]

        for item, value in kwargs.iteritems():
            if GiottoPrimitive in value.mro():
                kwargs[item] = self.get_primitive(value.__name__)

        for arg in args:
            kwargs[arg] = self.data(arg)

        return kwargs

    def get_response(self):
        model, view, controller = self.get_model_view_controller()
        model_data = model(**controller)
        if hasattr(view, 'render'):
            return view.render(model_data)
        else:
            return view(model_data)

class bind_controller_view(object):
    """
    Bind a controller tip to a view for the HTTP controller context
    """

    def __init__(self, controller, view):
        self.view = view
        self.controller = controller

    def __call__(self, controller_tip):
        argspec = inspect.getargspec(controller_tip)
        module = controller_tip.__module__
        name = controller_tip.__name__

        @wraps(controller_tip)
        def wrapper(**kwargs):
            return (self.view, controller_tip(**kwargs))

        n = module + "." + name
        app_map[self.controller][n] = {'app': wrapper, 'argspec': argspec}

        return controller_tip

def bind_model(model, cache=None):
    @decorator.decorator
    def inner_bind_model(controller_tip, *args, **kw):
        data = controller_tip(*args, **kw)
        return (model, data)

    return inner_bind_model





class GiottoProgram(object):
    name = ''
    model = lambda x: x
    view = lambda x: x

    def __init__(self, request):
        self.request = request

    def convert_to_real_app(self):
        """
        Convert this class into a 'real' giotto cntroller app, based on the
        controller attribute.
        """
        for controllers in get_all_controllers():
            if controller.name == self.name:
                return controller


class GiottoController(object):
    pass


class HTTPController(GiottoController):
    def __init__(self, generic):
        pass

    def get_response(self, request):
        c = self.get_controller_args(self.request)
        m = self.model(c)
        v = self.view(m)
        return GiottoResponse(v)



def itersubclasses(cls, _seen=None):
    """
    itersubclasses(cls)

    Generator over all subclasses of a given class, in depth first order.

    >>> list(itersubclasses(int)) == [bool]
    True
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(A): pass
    >>> class D(B,C): pass
    >>> class E(D): pass
    >>> 
    >>> for cls in itersubclasses(A):
    ...     print(cls.__name__)
    B
    D
    E
    C
    >>> # get ALL (new-style) classes currently defined
    >>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
    ['type', ...'tuple', ...]
    """
    
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None: _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError: # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub
















