from functools import wraps
from collections import defaultdict
import inspect
import decorator

controller_maps = defaultdict(lambda: {})

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
        controller_maps[self.controller][n] = {'app': wrapper, 'argspec': argspec}

        return controller_tip

def bind_model(model, cache=None):
    @decorator.decorator
    def inner_bind_model(controller_tip, *args, **kw):
        data = controller_tip(*args, **kw)
        return (model, data)

    return inner_bind_model



















