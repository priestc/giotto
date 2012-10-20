from giotto.views import BasicView
from giotto.models import make_tables

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
    name = "make_tables"
    controllers = ('cmd', )
    model = [make_tables]
    view = BasicView