import inspect
import json

from giotto.programs import GiottoProgram
from giotto.exceptions import InvalidInput, ProgramNotFound, MockNotFound, ControlMiddlewareInterrupt
from giotto.primitives import GiottoPrimitive
from giotto.keyvalue import DummyKeyValue

class GiottoController(object):
    middleware_interrupt = None
    
    def __init__(self, request, manifest, model_mock=False, errors=None):
        from giotto import config
        self.request = request
        self.model_mock = model_mock
        self.cache = config.cache or DummyKeyValue()
        self.errors = errors
        self.manifest = manifest

        # the program that corresponds to this invocation
        invocation = self.get_invocation()
        name = self.get_controller_name()
        parsed = self.manifest.parse_invocation(invocation, name)

        self.program = parsed['program']
        self.program.name = parsed['name']
        self.path_args = parsed['args']
        self.mimetype = parsed['superformat_mime'] or self.mimetype_override() or self.default_mimetype

    def get_response(self):
        control = None
        name = self.get_controller_name()
        try:
            self.request = self.program.execute_input_middleware_stream(self.request, name)
        except ControlMiddlewareInterrupt as exc:
            # A middleware class returned a control object, save it to the class.
            # The get_data_response method will use it.
            self.middleware_interrupt = exc.control

        response = self.get_concrete_response()

        return self.program.execute_output_middleware_stream(self.request, response, name)

    def get_data_response(self):
        """
        Execute the model and view, and handle the cache.
        Returns controller-agnostic response data.
        """
        if self.middleware_interrupt:
            return self.middleware_interrupt

        if self.model_mock:
            model_data = self.program.get_model_mock()
        else:
            args, kwargs = self.program.get_model_args_kwargs()
            data = self.get_data_for_model(args, kwargs)

            if self.program.cache and not self.errors:
                key = self.get_cache_key(data)
                hit = self.cache.get(key)
                if hit:
                    return hit
        
            model_data = self.program.execute_model(data)
        
        response = self.program.execute_view(model_data, self.mimetype, self.errors)

        if self.program.cache and not self.errors and not self.model_mock:
            self.cache.set(key, response, self.program.cache)

        return response

    def get_data_for_model(self, args, kwargs):
        """
        In comes args and kwargs expected for the model. Out comes the data from
        this invocation that will go to the model.
        """
        raw_data = self.get_raw_data()
        output = {}
        for i, arg in enumerate(args):
            if i < len(self.path_args):
                # use path args instead (if they have been supplied)
                target = self.path_args[i]
            else:
                target = raw_data.get(arg, None)

            output[arg] = target

        for key, value in kwargs.iteritems():
            if isinstance(value, GiottoPrimitive):
                output[key] = self.get_primitive(value.name)
            else:
                output[key] = value

        return output


    def __repr__(self):
        controller = self.get_controller_name()
        model = self.get_program_name()
        data = self.get_data()
        return "<%s %s - %s - %s>" % (  
            self.__class__.__name__, controller, model, data
        )

    def mimetype_override(self):
        """
        In some circumstances, the returned mimetype can be changed. Return that here.
        Otherwise the default or superformat will be used.
        """
        return None

    def get_cache_key(self, data):
        try:
            controller_args = json.dumps(data, separators=(',', ':'), sort_keys=True)
        except TypeError:
            # controller contains info that can't be json serialized:
            controller_args = str(data)

        program = self.program.name
        return "%s(%s)(%s)" % (controller_args, program, self.mimetype)
