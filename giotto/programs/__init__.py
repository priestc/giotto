import inspect
import re
import os

from giotto.exceptions import ProgramNotFound, MockNotFound, ControlMiddlewareInterrupt
from giotto.utils import super_accept_to_mimetype
from giotto.control import GiottoControl
from giotto.views import GiottoView

class GiottoProgram(object):
    name = None
    pre_input_middleware = ()
    input_middleware = ()
    controllers = ()
    cache = 0
    model = ()
    view = None
    output_middleware = ()

    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        if hasattr(self.view, 'mro') and GiottoView in self.view.mro():
            # instantiate all views that are defined as a class.
            self.view = self.view()

    def get_model_args_kwargs(self):
        """
        Inspect the model (or view in the case of no model) and return the args
        and kwargs. This functin is necessary because argspec returns in a silly format
        by default.
        """
        source = self.get_model()
        if not source:
            return [], {}

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

    def get_model(self):
        if len(self.model) == 0:
            return None
        return self.model[0]

    def has_mock_defined(self):
        return len(self.model) > 1

    def get_model_mock(self):
        if not self.model or not self.model[0]:
            # no mock needed
            return {}
        try:
            return self.model[1]
        except IndexError:
            raise MockNotFound("no mock for %s" % self.name)

    def execute_input_middleware_stream(self, request, controller):
        """
        Request comes from the controller. Returned is a request.
        controller arg is the name of the controller.
        """
        # either 'http' or 'cmd' or 'irc'
        controller_name = "".join(controller.get_controller_name().split('-')[:1])
        middlewares = list(self.pre_input_middleware) + list(self.input_middleware)
        for m in middlewares:
            to_execute = getattr(m(controller), controller_name)
            if to_execute:
                result = to_execute(request)
                if GiottoControl in type(result).mro():
                    # a middleware class returned a control object (redirection, et al.)
                    raise ControlMiddlewareInterrupt(control=result)
                request = result
        return request

    def execute_output_middleware_stream(self, request, response, controller):
        controller_name = "".join(controller.get_controller_name().split('-')[:1]) # 'http-get' -> 'http'
        for m in self.output_middleware:
            to_execute = getattr(m(controller), controller_name, None)
            if to_execute:
                response = to_execute(request, response)
        return response

    def execute_model(self, data):
        """
        Returns data from the model, if mock is defined, it returns that instead.
        """
        model = self.get_model()
        if model is None:
            return None
        return model(**data)

    def execute_view(self, data, mimetype, errors):
        if not self.view:
            return {'body': '', 'mimetype': ''}
        return self.view.render(data, mimetype, errors)

class ProgramManifest(object):
    """
    Represents a node in a larger manifest tree. Manifests are like URLS for
    giotto applications. All keys must be strings, and all values must be
    either GiottoPrograms or another ProgramManifest instance.
    """
    key_regex = r'^\w*$'

    def __init__(self, manifest, backname=None):
        self.manifest = manifest
        # any sub manifests, convert to manifests objects
        for key, item in self.manifest.items():
            type_ = type(item)

            is_program = isinstance(item, GiottoProgram)
            is_manifest = type_ == ProgramManifest
            is_list = type_ == list

            if not re.match(self.key_regex, key):
                raise ValueError("Invalid manifest key: %s" % key)

            if type_ is dict:
                self.manifest[key] = ProgramManifest(item, backname=key)
            elif not is_manifest and not is_program and not is_list:
                msg = "Manifest value must be either: a program, a list of programs, or another manifest"
                raise TypeError(msg)

    def __repr__(self):
        return "<Manifest %s (%s nodes)>" % (self.backname, len(self.manifest))

    def __getitem__(self, key):
        return self.manifest[key]

    def get_program(self, program_name, controller_tag):
        """
        Find the program within this manifest. If key is found, and it contains
        a list, iterate over the list and return the program that matches
        the controller tag. 
        """
        result = self.manifest[program_name]
        if type(result) == ProgramManifest:
            return result
        if type(result) is not list:
            result = [result]
        for program in result:
            if controller_tag in program.controllers:
                return program

        # we looped through all programs and found no match, maybe one program
        # has no explicitly defined controller tag? If so return that.
        for program in result:
            if not program.controllers or '*' in program.controllers:
                return program

        # we found the key, and looped through all programs, but the controller
        # tag could not be found.
        msg = "Program '%s' does not allow '%s' controller" % (program_name, controller_tag)
        raise ProgramNotFound(msg)

    def extract_superformat(self, name):
        """
        In comes the program name, out comes the superformat (html, json, xml, etc)
        and the new program name with superstring removed.
        """
        if '.' in name:
            splitted = name.split('.')
            return (splitted[0], splitted[1])
        else:
            return (name, None)

    def parse_invocation(self, invocation, controller_tag):
        if invocation.endswith('/'):
            invocation = invocation[:-1]
        if invocation.startswith('/'):
            invocation = invocation[1:]

        splitted_path = invocation.split('/')
        start_name = splitted_path[0]
        start_args = splitted_path[1:]

        parsed = self._parse(start_name, start_args, controller_tag)
        parsed['invocation'] = invocation
        return parsed

    def _parse(self, raw_program_name, args, controller_tag):
        """
        Recursive function to transversing nested manifests.
        raw_program_name == program with superformat intact
        """
        program_name, superformat = self.extract_superformat(raw_program_name)
        try:
            program = self.get_program(program_name, controller_tag)
        except KeyError:
            # program name is not in keys, drop down to root...
            if '' in self.manifest:
                result = self.get_program('', controller_tag)
                if type(result) == ProgramManifest:
                    return result._parse(raw_program_name, args, controller_tag)
                else:
                    return {
                        'program': result,
                        'name': '',
                        'superformat': superformat,
                        'superformat_mime': None,
                        'args': [program_name] + args,
                    }
            else:
                raise ProgramNotFound("Program '%s' Does Not Exist" % program_name)
        else:
            if type(program) == ProgramManifest:
                if program_name == '':
                    return program._parse('', args, controller_tag)
                if not args:
                    raise ProgramNotFound('No root program for namespace, and no program match')
                return program._parse(args[0], args[1:], controller_tag)
            else:
                return {
                    'program': program,
                    'name': program_name,
                    'superformat': superformat,
                    'superformat_mime': super_accept_to_mimetype(superformat),
                    'args': args,
                }

from giotto.programs.shell import Shell
from giotto.programs.make_tables import MakeTables
management_manifest = ProgramManifest({
    'make_tables': MakeTables(),
    'shell': Shell(),
})