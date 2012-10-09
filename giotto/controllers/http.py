from werkzeug.wrappers import Request, Response
from giotto import GiottoAbstractProgram, GiottoProgram
from giotto.core import GiottoHttpException, GiottoApp
from giotto.exceptions import InvalidInput

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
        return "<%s %s - %s - %s>" % (self.__class__.__name__, controller, model, data)

    def _get_program(self):
        """
        Search through all installed programs and return the one that matches
        this request.
        """
        for p in self.programs:
            name_match = p.name == self.get_program_name()
            controller_match = p.controller == self.get_controller_name()
            if name_match and controller_match:
                return p

        raise Exception("Can't find program for: %s in: %s" % (
            self.__repr__(), self.show_program_names())
        )

    def _get_generic_response_data(self):
        """
        Return the data to create a response object appropriate for the
        controller. This function is called by get_concrete_response_data
        """
        raw_data = self.get_data()
        model = getattr(self.program, 'model', None)
        view = self.program.view

        if model:
            data = self.get_primitives(model, raw_data)
            view_data = model[0](**data)
        else:
            view_data = self.get_primitives(view, raw_data)

        return self.render_view(view_data)

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
            disp = "%s - %s" % (p.name, p.controller)
            out.append(disp)
        return "\n".join(out)

    def render_view(self, view_data):
        """
        Render the view with data from the model and/or controller.
        """
        if hasattr(self.program.view, 'render'):
            response = self.program.view.render(view_data)
        else:
            response = self.program.view(view_data)

        return response

class HTTPController(GiottoController):
    name = 'http'

    def get_program_name(self):
        return self.request.path[1:].replace('/', '.')

    def get_controller_name(self):
        return 'http-%s' % self.request.method.lower()

    def get_data(self):
        data = {}
        if self.request.method == 'GET':
            data = self.request.args
        elif self.request.method == 'POST':
            data = self.request.form
        return data

    def get_concrete_response(self):
        result = self._get_generic_response_data()

        # convert to a format appropriate to the wsgi Response api.
        response = Response(
            response=result['body'],
            mimetype=result['mimetype'],
        )

        # now do middleware
        return self.execute_output_middleware_stream(response) 

    def get_primitives(self, source, raw_data):
        return raw_data

def make_app(programs):
    
    def application(environ, start_response):
        """
        WSGI app for serving giotto applications
        """
        request = Request(environ)
        controller = HTTPController(request, programs)
        wsgi_response = controller.get_concrete_response()
        return wsgi_response(environ, start_response)

    return application

















