import inspect

from giotto import GiottoAbstractProgram, GiottoProgram
from giotto.exceptions import InvalidInput
from giotto.primitives import GiottoPrimitive

def do_argspec(source):
    if hasattr(source, 'render'):
        # if 'source' is a view object, try to get the render method,
        # otherwise, just use the __call__ method.
        source = source.render

    argspec = inspect.getargspec(source)
    kwargs = dict(zip(*[reversed(l) for l in (argspec.args, argspec.defaults or [])]))
    args = [x for x in argspec.args if x not in kwargs.keys()]
    return args, kwargs

class GiottoController(object):
    def __init__(self, request, programs):
        self.request = request

        # all programs available to this controller
        self.programs = []
        for p in programs:
            first_two = p.mro()[0:2]
            if GiottoAbstractProgram not in first_two:
                # exclude abstract programs
                self.programs.append(p)

        # the program that corresponds to this invocation
        self.program = self._get_program()

        self.execute_input_middleware_stream()

    def __repr__(self):
        controller = self.get_controller_name()
        model = self.get_program_name()
        data = self.get_data()
        return "<%s %s - %s - %s>" % (
            self.__class__.__name__, controller, model, data
        )

    def _get_program(self):
        """
        Search through all installed programs and return the one that matches
        this request.
        """
        for p in self.programs:
            controller = self.get_controller_name()
            name = self.get_program_name()
            if p.is_match(controller, name):
                return p

        raise Exception("Can't find program for: %s in: %s" % (
            self.__repr__(), self.show_program_names())
        )

    def _get_generic_response_data(self):
        """
        Return the data to create a response object appropriate for the
        controller. This function is called by get_concrete_response_data.
        """
        raw_data = self.get_data()
        # model is defined in the program as a one-item tuple
        model = getattr(self.program, 'model', [None])[0]
        view = self.program.view
        if model:
            data = self.get_model_args(model, raw_data)
            view_data = model(**data)
        else:
            # there is no model, so we will use the view as the model.
            view_data = self.get_model_args(view, raw_data)

        return self.render_view(view_data)

    def get_mimetype(self):
        return self.default_mimetype

    def get_model_args(self, source, raw_data):
        """
        Given raw data from the controller, inspect the model function (or in
        the case of a program that has no model, the view object) and replace
        all primitives with appropriate data.
        """
        args, kwargs = do_argspec(source)
        output = {}
        for arg in args:
            target = raw_data.get(arg, None)
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

    def show_program_names(self):
        """
        Print out a list of all program names for debugging purposes
        """
        out = []
        for p in self.programs:
            disp = "%s - %s" % (p.name, p.controllers)
            out.append(disp)
        return "\n".join(out)

    def render_view(self, view_data):
        """
        Render the view with data from the model and/or controller.
        """
        ViewClass = self.program.view[0]
        view = ViewClass(view_data)

        response = view.render(self.get_mimetype())

        return response
