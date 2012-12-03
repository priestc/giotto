import inspect
import json

from giotto.programs import GiottoProgram
from giotto.exceptions import InvalidInput, ProgramNotFound, MockNotFound
from giotto.primitives import GiottoPrimitive

def do_argspec(source):
    """
    Inspect the model (or view in the case of no model) and return the args
    and kwargs. This functin is necessary because argspec returns in a silly format
    by default.
    """
    if hasattr(source, 'render'):
        # if 'source' is a view object, try to get the render method,
        # otherwise, just use the __call__ method.
        source = source.render

    argspec = inspect.getargspec(source)
    kwargs = dict(zip(*[reversed(l) for l in (argspec.args, argspec.defaults or [])]))
    args = [x for x in argspec.args if x not in kwargs.keys()]
    if args and args[0] == 'cls':
        args = args[1:]
    return args, kwargs

class GiottoController(object):
    def __init__(self, request, manifest, model_mock=False):
        from giotto import config
        self.request = request
        self.model_mock = model_mock
        self.cache = config.cache

        # all programs available to this controller
        self.manifest = manifest

        # the program that corresponds to this invocation
        invocation = self.get_invocation()
        parsed = self.manifest.parse_invocation(invocation)

        self.program = parsed['program']
        self.path_args = parsed['args']
        self.mimetype = parsed['superformat_mime'] or self.mimetype_override() or self.default_mimetype

    def __repr__(self):
        controller = self.get_controller_name()
        model = self.get_program_name()
        data = self.get_data()
        return "<%s %s - %s - %s>" % (
            self.__class__.__name__, controller, model, data
        )

    def mimetype_override(self):
        """
        In some circumstances, the returned mimetype can be changed. Return that here.
        Otherwise the default or superformat will be used.
        """
        return None

    def get_cache_key(self):
        data = self.get_model_args(self.get_model(), self.get_data())
        try:
            controller_args = json.dumps(data, separators=(',', ':'), sort_keys=True)
        except TypeError:
            # controller contains info that can't be json serialized:
            controller_args = str(data)

        program = self.program.name
        return "%s(%s)(%s)" % (controller_args, program, self.mimetype)

    def get_model_mock(self):
        try:
            return self.program.model[1]
        except IndexError:
            # if no mock is defined, then use an empty dict as the data
            return {}

    def _get_generic_response_data(self):
        """
        Return the data to create a response object appropriate for the
        controller. This function is called by get_concrete_response_data.
        """
        self.execute_input_middleware_stream()

        cache_key = self.get_cache_key()
        raw_data = self.get_data()
        model = self.get_model()
        view = self.program.view
        
        if self.model_mock:
            # if the model mock option is True, then bypass the model
            # and just return the mock
            return self.render_view(self.get_model_mock())

        if self.program.cache:
            rendered = self.cache.get(cache_key)
            if rendered:
                # return hit from cache
                return rendered

        if model:
            data = self.get_model_args(model, raw_data)
            view_data = model(**data)
        else:
            # there is no model, so we will use the view as the model.
            view_data = self.get_model_args(view, raw_data)

        rendered = self.render_view(view_data)

        if self.program.cache:
            self.cache.set(cache_key, rendered, self.program.cache)

        return rendered

    def get_model(self):
        if self.program.model:
            # remove ugly wrapping list (to avoid becoming an instance mothod
            return self.program.model[0]
        else:
            return lambda: {}

    def get_model_args(self, source, raw_data):
        """
        Given raw data from the controller, inspect the model function (or in
        the case of a program that has no model, the view object) and replace
        all primitives with appropriate data.
        """
        if self.model_mock:
            return {}
        args, kwargs = do_argspec(source)
        output = {}
        for i, arg in enumerate(args):
            if i < len(self.path_args):
                # use path args instead (if they have been supplied)
                pa = self.path_args[i]
            else:
                pa = None
            target = pa or raw_data.get(arg, None)
            output[arg] = target

        for key, value in kwargs.iteritems():
            if isinstance(value, GiottoPrimitive):
                output[key] = self.get_primitive(value.name)
            else:
                output[key] = value

        return output

    def execute_input_middleware_stream(self):
        middlewares = getattr(self.program, 'input_middleware', [])
        for m in middlewares:
            to_execute = getattr(m(), self.name)
            self.request = to_execute(self.request)
        return self.request

    def execute_output_middleware_stream(self, response):
        middlewares = getattr(self.program, 'output_middleware', [])
        for middleware_class in middlewares:
            middleware_instance = middleware_class()
            to_execute = getattr(middleware_instance, self.name, None)
            if to_execute:
                response = to_execute(self.request, response)
        return response

    def render_view(self, view_data):
        """
        Render the view with data from the model and/or controller.
        """
        ViewClass = self.program.view
        view = ViewClass(view_data, self)
        response = view.render(self.mimetype)
        return response
