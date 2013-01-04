import inspect
import json

from giotto.programs import GiottoProgram
from giotto.exceptions import (GiottoException, InvalidInput, ProgramNotFound,
    MockNotFound, ControlMiddlewareInterrupt, NotAuthorized)
from giotto.primitives import GiottoPrimitive
from giotto.keyvalue import DummyKeyValue
from giotto.control import GiottoControl

class GiottoController(object):
    middleware_interrupt = None
    persist_data = None

    def __init__(self, request, manifest, model_mock=False, errors=None):
        from giotto import config
        self.request = request
        self.model_mock = model_mock
        self.cache = config.cache or DummyKeyValue()
        self.errors = errors
        self.manifest = manifest
        self.middleware_interrupt_exc = None
        self.middleware_control = None

        # the program that corresponds to this invocation
        invocation = self.get_invocation()
        name = self.get_controller_name()
        parsed = self.manifest.parse_invocation(invocation, name)

        self.program = parsed['program']
        self.program.name = parsed['name']
        self.path_args = parsed['args']
        self.mimetype = parsed['superformat_mime'] or self.mimetype_override() or self.default_mimetype

    def get_response(self):
        try:
            last_good_request, middleware_result = self.program.execute_input_middleware_stream(self.request, self)
        except GiottoException as exc:
            # save this exception so it can be re-raised from within
            # get_data_response() so that get_concrete_response() can handle it
            self.middleware_interrupt_exc = exc
            self.request = last_good_request
        else:
            self.request = middleware_result # middleware ended cleanly

        if GiottoControl in type(middleware_result).mro():
            # middleware returned a control object
            self.middleware_control = middleware_result
            self.request = last_good_request

        response = self.get_concrete_response()

        if self.persist_data:
            response = self.persist(self.persist_data, response)

        return self.program.execute_output_middleware_stream(self.request, response, self)

    def get_data_response(self):
        """
        Execute the model and view, and handle the cache.
        Returns controller-agnostic response data.
        """
        if self.middleware_interrupt_exc:
            ## the middleware raised an exception, re-raise it here so
            ## get_concrete_response (defined in subclasses) can catch it.
            raise self.middleware_interrupt_exc

        if self.middleware_control:
            ## this redirect object came from middleware but return it as if it
            ## came from a view.
            return {'body': self.middleware_control}

        if self.model_mock and self.program.has_mock_defined():
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

        if 'persist' in response:
            self.persist_data = response['persist']

        return response

    def get_data_for_model(self, args, kwargs):
        """
        In comes args and kwargs expected for the model. Out comes the data from
        this invocation that will go to the model.
        In other words, this function does the 'data negotiation' between the
        controller and the model.
        """
        raw_data = self.get_raw_data()
        defaults = kwargs
        values = args + list(kwargs.keys())

        output = {}
        i = -1
        for i, value in enumerate(values):
            if value in defaults:
                may_be_primitive = defaults[value]
                if isinstance(may_be_primitive, GiottoPrimitive):
                    output[value] = self.get_primitive(may_be_primitive.name)
                    continue # don't let user input override primitives.
                else:
                    output[value] = may_be_primitive

            if i + 1 <= len(self.path_args):
                output[value] = self.path_args[i]
            if value in raw_data:
                output[value] = raw_data[value]

        if len(self.path_args) > i + 1:
            raise ProgramNotFound("Too many positional arguments for program: '%s'" % self.program.name)

        if not len(output) == len(values):
            raise ProgramNotFound("Not enough data for program '%s'" % self.program.name)

        return output

    def persist(self, values):
        """
        Persist this data between the user and the server.
        """
        raise NotImplementedError

    def __repr__(self):
        controller = self.get_controller_name()
        model = self.program.name
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
