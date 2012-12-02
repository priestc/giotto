from giotto.views import BasicView
from giotto.models import make_tables
from giotto.primitives import ALL_PROGRAMS
from giotto.exceptions import ProgramNotFound

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

class ProgramManifest(object):
    def __init__(self, manifest):
        self.manifest = manifest
        # any sub manifests, convert to manifests objects
        for key, item in self.manifest.items():
            if type(item) is dict:
                self.manifest[key] = ProgramManifest(item)

    def __repr__(self):
        return "<Manifest (%s nodes)>" % len(self.manifest)

    def __getitem__(self, key):
        return self.manifest[key]

    def get_program(self, path):
        if path.endswith('/'):
            path = path[:-1]
        splitted_path = path.split('/')
        program_name = splitted_path[0]
        args = splitted_path[1:]

        program, args = self._get_program(program_name, args)
        
        if args:
            p = splitted_path[:len(args)*-1]
        else:
            p = splitted_path

        program.path = "/".join(p)
        program.name = p[-1]
        return program, args

    def _get_program(self, program, args):
        """
        Recursive function to transversing nested manifests
        """
        try:
            program = self[program]
            if type(program) == ProgramManifest:
                if not args:
                    raise ProgramNotFound('Namespace found, but no program')
                return program._get_program(args[0], args[1:])
            else:
                return program, args
        except KeyError:
            raise ProgramNotFound('Program %s Does Not Exist' % program)














