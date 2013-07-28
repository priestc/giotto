from collections import deque
import inspect
import json

from giotto import get_config
from giotto.programs import GiottoProgram
from giotto.exceptions import (GiottoException, InvalidInput, ProgramNotFound,
    MockNotFound, ControlMiddlewareInterrupt, NotAuthorized)
from giotto.primitives import GiottoPrimitive, RAW_INVOCATION_ARGS
from giotto.keyvalue import DummyKeyValue
from giotto.control import GiottoControl

class GiottoController(object):
    middleware_interrupt = None
    persist_data = None

    def __init__(self, request, manifest, model_mock=False, errors=None):
        self.request = request
        self.model_mock = model_mock
        self.cache = get_config('cache_engine', DummyKeyValue())
        self.errors = errors
        self.manifest = manifest
        self.middleware_interrupt_exc = None
        self.middleware_control = None
        self.display_data = 'Not calculated yet'
        
        # the program that corresponds to this invocation
        invocation = self.get_invocation()
        name = self.get_controller_name()
        parsed = self.manifest.parse_invocation(invocation, controller_tag=name)

        self.raw_args = parsed['raw_args']
        self.program = parsed['program']
        self.program.name = parsed['program_name']
        self.path_args = parsed['args']
        if parsed['superformat']:
            self.mimetype = parsed['superformat_mime'] or parsed['superformat']
        else:
            self.mimetype = self.mimetype_override() or self.default_mimetype

    def get_response(self):
        """
        High level function for getting a response. This is what the concrete
        controller should call. Returns a controller specific response.
        """
        last_good_request = self.request
        middleware_result = None
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
            self.display_data = data # just for displaying in __repr__

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
        kwargs_from_invocation = self.get_raw_data()
        args_from_invocation = deque(self.path_args)

        defaults = kwargs
        values = args + list(kwargs.keys())

        output = {}

        raw = False
        for i, field in enumerate(values):
            ## going through each bit of data that the model needs
            ## `field` here is the name of each needed var.

            # the 'default' value that may be defined in the model.
            # this variable might be a string or int or might even be a primitive object.
            # NotImplemented here is used as to preserve if a default value is None.
            # it is used here as a sort of MetaNone.
            default_defined_in_model = defaults.get(field, NotImplemented)
            
            # the value in kwarg arguments such as --values and GET params
            from_data_kwargs = kwargs_from_invocation.get(field, None)

            # The value that will end up being used.
            value_to_use = None

            if default_defined_in_model == RAW_INVOCATION_ARGS:
                # flag that the RAW_INVOCATION_ARGS primitive has been invoked
                # used later to suppress errors for unused program args
                # when this primitive is invoked, all positional args are invalid. 
                raw = True

            if type(default_defined_in_model) == GiottoPrimitive:
                value_to_use = self.get_primitive(default_defined_in_model.name)
            elif from_data_kwargs:
                value_to_use = from_data_kwargs
            elif not raw and args_from_invocation:
                value_to_use = args_from_invocation.popleft()
            elif default_defined_in_model is not NotImplemented:
                value_to_use = default_defined_in_model
            else:
                raise Exception("Data Missing For Program. Missing: %s" % field)
            
            output[field] = value_to_use

        if args_from_invocation and not raw:
            raise Exception("Too many argumets to program: %s" % args_from_invocation)

        return output

    def persist(self, values):
        """
        Persist this data between the user and the server.
        """
        raise NotImplementedError("This controller does not support persistance")

    def __repr__(self):
        controller = self.get_controller_name()
        model = self.program.name
        data = self.display_data
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
