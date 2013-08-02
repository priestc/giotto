import inspect
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict # python2.6

import re
import os

from giotto.exceptions import ProgramNotFound, MockNotFound, ControlMiddlewareInterrupt, NoViewMethod
from giotto.utils import super_accept_to_mimetype
from giotto.control import GiottoControl
from giotto.views import GiottoView

class Program(object):
    name = None
    description = None
    tests = []
    pre_input_middleware = ()
    input_middleware = ()
    controllers = ()
    cache = 0
    model = ()
    view = None
    output_middleware = ()

    valid_args = [
        'name', 'description', 'tests', 'pre_input_middleware', 'controllers',
        'input_middleware', 'cache', 'model', 'view', 'output_middleware'
    ]

    def __repr__(self):
        return "<Program: %s>" % self.name

    def __init__(self, description=None, **kwargs):
        self.description = description
        for k, v in kwargs.items():
            if k not in self.valid_args:
                raise ValueError(
                    "Invalid Program argument: '%s'. Choices are: %s" %
                    (k, ", ".join(self.valid_args))
                )
            else:
                setattr(self, k, v)

        if hasattr(self.view, 'mro') and GiottoView in self.view.mro():
            # instantiate all views that are defined as a class.
            self.view = self.view()

        m = self.get_model()
        self.name = (m and m.__name__) or kwargs.get('name')

    def get_model_args_kwargs(self):
        """
        Inspect the model (or view in the case of no model) and return the args
        and kwargs. This functin is necessary because argspec returns in a silly format
        by default.
        """
        source = self.get_model()
        if not source:
            return [], {}

        argspec = inspect.getargspec(source)
        
        kk = list(zip(*[reversed(l) for l in (argspec.args, argspec.defaults or [])]))
        kk.reverse()
        kwargs = OrderedDict(kk)
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
        start_request = request
        # either 'http' or 'cmd' or 'irc'
        controller_name = "".join(controller.get_controller_name().split('-')[:1])
        middlewares = list(self.pre_input_middleware) + list(self.input_middleware)
        for m in middlewares:
            to_execute = getattr(m(controller), controller_name)
            if to_execute:
                result = to_execute(request)
                if GiottoControl in type(result).mro():
                    # a middleware class returned a control object (redirection, et al.)
                    # ignore all other middleware classes
                    return request, result
                request = result
        return start_request, request

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

key_regex = re.compile(r'^\w*$')

class Manifest(object):
    """
    Represents a node in a larger manifest tree. Manifests are like URLS for
    giotto applications. All keys must be strings, and all values must be
    either Programs or another Manifest instance.
    """
    
    def __repr__(self):
        return "<Manifest %s (%s nodes)>" % (self.backname, len(self.manifest))

    def __getitem__(self, key):
        return self.manifest[key]

    def __init__(self, manifest, backname='root'):
        self.backname = backname
        self.manifest = manifest
        # any sub manifests, convert to manifests objects
        for key, item in self.manifest.items():
            type_ = type(item)

            is_program = isinstance(item, Program)
            is_manifest = type_ == Manifest
            is_list = type_ == list
            is_str = type_ == str

            if not key_regex.match(key):
                raise ValueError("Invalid manifest key: %s" % key)

            if type_ is dict:
                self.manifest[key] = Manifest(item, backname=key)
            elif not any([is_manifest, is_program, is_list, is_str]):
                msg = "Manifest value must be either: a program, a list of programs, or another manifest"
                raise TypeError(msg)

    def get_urls(self, controllers=None, prefix_path=''):
        """
        Return a list of all valid urls (minus args and kwargs, just the program paths)
        for this manifest. If a single program has two urls, both will be returned.
        """
        tag_match = lambda program: set(program.controllers) & set(controllers or [])
        urls = set()

        for key, value in self.manifest.items():

            path = "%s/%s" % (prefix_path, key)

            if path.endswith('/') and prefix_path:
                path = path[:-1]

            if hasattr(value, 'lower'):
                # is a string redirect
                urls.add(path)

            elif isinstance(value, Manifest):
                # is manifest
                pp = '' if path == '/' else path # for 'stacked' root programs.
                new_urls = value.get_urls(controllers=controllers, prefix_path=pp)
                urls.update(new_urls)

            elif isinstance(value, Program):
                # make a list so we can iterate through it in the next `if` block
                value = [value]

            if hasattr(value, 'append'):
                # defined is multiple programs, get the one for this controller tag.
                for program in value:
                    if not program.controllers or not controllers:
                        # no controllers defined on program. Always add.
                        # or no tags defined for this get_urls call. Always add.
                        urls.add(path)
                    elif tag_match(program):
                        urls.add(path)

        return urls

    def _get_suggestions(self, filter_word=None):
        """
        This only gets caled internally from the get_suggestion method.
        """
        keys = self.manifest.keys()
        words = []
        for key in keys:            
            if isinstance(self.manifest[key], Manifest):
                # if this key is another manifest, append a slash to the 
                # suggestion so the user knows theres more items under this key
                words.append(key + '/')
            else:
                words.append(key)

        if filter_word:
            words = [x for x in words if x.startswith(filter_word)]

        return words

    def get_suggestion(self, front_path):
        """
        Returns suggestions for a path. Used in tab completion from the command
        line.
        """
        if '/' in front_path:
            # transverse the manifest, return the new manifest, then
            # get those suggestions with the remaining word
            splitted = front_path.split('/')
            new_manifest = self.manifest
            pre_path = ''
            for item in splitted:
                try:
                    new_manifest = new_manifest[item]
                except KeyError:
                    partial_word = item
                    break
                else:
                    pre_path += item + '/'

            if isinstance(new_manifest, Program):
                return []
            matches = new_manifest._get_suggestions(partial_word)
            return [pre_path + match for match in matches]
        else:
            return self._get_suggestions(front_path or None)

    def get_program(self, program_path, controller=None):
        """
        Find the program within this manifest. If key is found, and it contains
        a list, iterate over the list and return the program that matches
        the controller tag. NOTICE: program_path must have a leading slash.
        """
        if not program_path or program_path[0] != '/':
            raise ValueError("program_path must be a full path with leading slash")

        items = program_path[1:].split('/')
        result = self
        for item in items:
            result = result[item]

        if hasattr(result, "lower"):
            # string redirect
            return self.get_program(result)

        elif type(result) is Manifest:
            return result.get_program('/')

        elif hasattr(result, 'append'):
            matching_blank = []
            for program in result:
                if controller in program.controllers:
                    return program
            
                if not program.controllers or not controller:
                    # no exact matching controllers for this program.
                    # Use the first controller with no
                    matching_blank.append(program)
            if matching_blank:
                return matching_blank[0]
            else:
                raise ProgramNotFound("No matcning program for %s controller" % controller)

        return result

    def parse_invocation(self, invocation, controller_tag):
        """
        Given an invocation string, determine which part is the path, the program,
        and the args.
        """
        if invocation.endswith('/'):
            invocation = invocation[:-1]
        if not invocation.startswith('/'):
            invocation = '/' + invocation
        if invocation == '':
            invocation = '/'

        all_programs = self.get_urls(controllers=[controller_tag])

        matching_paths = set()
        for program_path in sorted(all_programs):
            if invocation.startswith(program_path):
                matching_paths.add(program_path)

        longest = ""
        for path in matching_paths:
            longest = path if len(path) > len(longest) else longest

        matching_path = longest

        program = self.get_program(matching_path, controller=controller_tag)

        if not matching_path:
            raise ProgramNotFound("Can't find %s" % invocation)

        program_name = matching_path.split('/')[-1]
        path = "/".join(matching_path.split('/')[:-1]) + '/'
        args_fragment = invocation[len(matching_path):]

        superformat = None
        if args_fragment.startswith('.'):
            # args_fragment will be something like ".html/arg1/arg2" or just ".html"
            superformat = args_fragment.split('/')[0][1:]
            args = args_fragment.split('/')[1:]
            args_fragment = '/'.join(args)
        else:
            args = args_fragment.split("/")[1:] if args_fragment else []
            args_fragment = args_fragment[1:] if (args_fragment and args_fragment[0] =='/') else args_fragment

        return {
            'program': program,
            'program_name': program_name,
            'superformat': superformat,
            'superformat_mime': super_accept_to_mimetype(superformat),
            'args': args,
            'raw_args': args_fragment,
            'path': path,
            'invocation': invocation,
        }