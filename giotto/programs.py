from giotto.views import BasicView
from giotto.models import make_tables
from giotto.primitives import ALL_PROGRAMS
from giotto.exceptions import ProgramNotFound
from giotto.utils import super_accept_to_mimetype

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

    def extract_superformat(self, name):
        """
        In comes the program name, out comes the superformat (html, json, xml, etc)
        and the new program name with superstring removed.
        """
        if '.' in name:
            splitted = name.split('.')
            if len(splitted) > 2:
                raise ProgramNotFound('Invalid Program name: %' % name)
            return (splitted[0], splitted[1])
        else:
            return (name, None)

    def parse_invocation(self, invocation):
        if invocation.endswith('/'):
            invocation = invocation[:-1]
        if invocation.startswith('/'):
            invocation = invocation[1:]

        splitted_path = invocation.split('/')
        start_name = splitted_path[0]
        start_args = splitted_path[1:]

        parsed = self._parse(start_name, start_args)
        parsed['invocation'] = invocation
        return parsed

    def _parse(self, program_name, args):
        """
        Recursive function to transversing nested manifests
        """
        program_name, superformat = self.extract_superformat(program_name)
        try:
            program = self[program_name]
        except KeyError:
            # maybe program_name is supposed to be an arg to a root program?
            if '' in self.manifest:
                return {
                    'program': self[''],
                    'name': '',
                    'superformat': None,
                    'superformat_mime': None,
                    'args': [program_name] + args,
                }
            raise ProgramNotFound('Program %s Does Not Exist' % program_name)
        else:
            if type(program) == ProgramManifest:
                if not args:
                    raise ProgramNotFound('Namespace found, but no program')
                return program._parse(args[0], args[1:])
            else:
                return {
                    'program': program,
                    'name': program_name,
                    'superformat': superformat,
                    'superformat_mime': super_accept_to_mimetype(superformat),
                    'args': args,
                }