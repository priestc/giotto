from giotto.views import BasicView
from giotto.models import make_tables
from giotto.primitives import ALL_PROGRAMS

class GiottoProgram(object):
    name = None
    input_middleware = ()
    controllers = ()
    cache = 0
    model = ()
    view = ()
    output_middleware = ()

    @classmethod
    def is_match(cls, controller, name):
        """
        Does this program match the current invocation prameters? 
        """
        return cls.name == name and controller in cls.controllers

class MakeTables(GiottoProgram):
    """
    Program for creating the database tables for all imported models. Use this
    program internaly only. Do not hook it up through HTTP.
    """
    name = "make_tables"
    controllers = ('cmd', )
    model = [make_tables]
    view = BasicView

def show_programs(programs=ALL_PROGRAMS):
    return programs

class ShowAllPrograms(GiottoProgram):
    """
    Display a list of all instaled programs for all controllers for the
    currently invoked application.
    """
    name = "show_programs"
    controllers = ('http-get', 'cmd', 'irc')
    model = [show_programs]
    view = BasicView