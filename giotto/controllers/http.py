from werkzeug.wrappers import Request, Response
from giotto.core import GiottoHttpException, GiottoApp, config
from giotto.exceptions import InvalidInput

global config

class GiottoController(object):
    def __init__(self, request, programs):
        self.request = request
        self.programs = list(programs)

    def get_program(self):
        """
        Search through all installed programs and return the one that matches
        this request.
        """
        for p in self.programs:
            name_match = p.name == self.get_program_name()
            controller_match = p.controller == self.get_controller()
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
        program = self.get_program()

        raw_data = self.get_data()
        model = getattr(program, 'model', None)
        view = program.view

        if model:
            data = self.get_primitives(model, raw_data)
            view_data = model[0](**data)
        else:
            view_data = self.get_primitives(view, raw_data)

        return self.render_view(view_data)

    def show_program_names(self):
        """
        Print out a list of all program names for debugging purposes
        """
        out = []
        print list(self.programs)
        for p in self.programs:
            disp = "%s - %s" % (p.name, p.controller)
            out.append(disp)
        return "\n".join(out)

class HTTPController(GiottoController):

    def __repr__(self):
        controller = self.get_controller()
        model = self.get_program_name()
        data = self.get_data()
        return "<%s %s - %s - %s>" % (self.__class__.__name__, controller, model, data)

    def get_program_name(self):
        return self.request.path[1:].replace('/', '.')

    def get_controller(self):
        return 'http-%s' % self.request.method.lower()

    def get_data(self):
        data = {}
        if self.request.method == 'GET':
            data = self.request.args
        elif self.request.method == 'POST':
            data = self.request.form
        return data

    def get_concrete_response_data(self):
        result = self._get_generic_response_data()

        # convert to a format appropriate to the wsgi Response api.
        return {
            'response': result['body'],
            'mimetype': result['mimetype']
        }

    def render_view(self, view_data):
        """
        Render the view with data from the model and/or controller.
        """
        program = self.get_program()

        if hasattr(program.view, 'render'):
            response = program.view.render(view_data)
        else:
            response = program.view(view_data)

        return response

    def get_primitives(self, source, raw_data):
        return raw_data

def make_app(programs):
    
    def application(environ, start_response):
        """
        WSGI app for serving giotto applications
        """
        request = Request(environ)
        controller = HTTPController(request, programs)
        response_data = controller.get_concrete_response_data()
        wsgi_response = Response(**response_data)
        return wsgi_response(environ, start_response)

    return application

















