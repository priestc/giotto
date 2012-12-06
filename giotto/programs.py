import inspect
import re

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
    def get_model_args_kwargs(cls):
        """
        Inspect the model (or view in the case of no model) and return the args
        and kwargs. This functin is necessary because argspec returns in a silly format
        by default.
        """
        source = cls.get_model()
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

    @classmethod
    def get_model(cls):
        return cls.model[0]

    @classmethod
    def get_model_mock(cls):
        return cls.model[1]

    @classmethod
    def execute_input_middleware_stream(cls, request, controller):
        """
        Request comes from the controller. Returned is a request.
        controller arg is the name of the controller.
        """
        for m in cls.input_middleware:
            to_execute = getattr(m(), controller)
            if to_execute:
                request = to_execute(request)
        return request

    @classmethod
    def execute_output_middleware_stream(cls, request, response, controller):
        for m in cls.output_middleware:
            to_execute = getattr(m(), controller, None)
            if to_execute:
                response = to_execute(request, response)
        return response

    @classmethod
    def execute_model(cls, data):
        """
        Returns data from the model, if mock is defined, it returns that instead.
        """
        #if len(cls.model) == 1:
        return cls.model[0](**data)

    @classmethod
    def execute_view(cls, data, mimetype):
        return cls.view(data).render(mimetype)

class ProgramManifest(object):
    """
    Represents a node in a larger manifest tree. Manifests are like URLS for
    giotto applications. All keys must be strings, and all values must be
    either GiottoPrograms or another ProgramManifest instance.
    """
    key_regex = r'^\w*$'

    def __init__(self, manifest):
        self.manifest = manifest
        # any sub manifests, convert to manifests objects
        for key, item in self.manifest.items():
            type_ = type(item)
            
            is_program = (hasattr(item, 'mro') and GiottoProgram in item.mro())
            is_manifest = type_ == ProgramManifest

            if not re.match(self.key_regex, key):
                raise ValueError("Invalid manifest key: %s" % key)

            if type_ is dict:
                self.manifest[key] = ProgramManifest(item)
            elif not is_manifest and not is_program:
                raise TypeError("Manifest value must be either a program or another manifest")

    def __repr__(self):
        return "<Manifest (%s nodes)>" % len(self.manifest)

    def __getitem__(self, key):
        return self.manifest[key]

    def get_all_programs(self):
        """
        Tranverse this manifest and return all programs exist in this manifest.
        """
        out = set()
        programs = self.manifest.values()
        for program in programs:
            if type(program) == ProgramManifest:
                program_set = program.get_all_programs()
            else:
                program_set = set([program])
            out.update(program_set)

        return out

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
            # program name is not in keys, drop down to root...
            if '' in self.manifest:
                result = self['']
                if type(result) == ProgramManifest:
                    return result._parse(program_name, args)
                else:
                    return {
                        'program': result,
                        'name': '',
                        'superformat': None,
                        'superformat_mime': None,
                        'args': [program_name] + args,
                    }
            else:
                raise ProgramNotFound('Program %s Does Not Exist' % program_name)
        else:
            if type(program) == ProgramManifest:
                if program_name == '':
                    return program._parse('', args)
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