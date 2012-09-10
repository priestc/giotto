from functools import wraps
from collections import defaultdict
import inspect

controller_maps = defaultdict(lambda: {})

class bind_controller(object):
    """
    Bind a model method to a view for the HTTP controller context
    """

    def __init__(self, controller, view):
        self.view = view
        self.controller = controller

    def __call__(self, func):

        argspec = inspect.getargspec(func)
        module = func.__module__
        name = func.func_code.co_name

        @wraps(func)
        def wrapper(**kwargs):
            return self.view(func(**kwargs))

        n = module + "." + name
        controller_maps[self.controller][n] = {'app': wrapper, 'argspec': argspec}

        return func