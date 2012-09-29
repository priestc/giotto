# the config file of the project that giotto is handling
config = None

class GiottoHttpException(Exception):
    pass

def execute_input_middleware_stream(controller, stream):
    def get(item):
        pass
    classes = [get(item) for item in stream]

class GiottoApp(object):
    """
    Base class for all Giotto application controllers.
    """

    def get_controller_tip_path(self):
        raise NotImplementedError

    def get_model_view_controller(self):
        """
        Calculate the controller tip, then return the model, view, and controller
        along with the primitives filled in.
        """
        ctp = self.get_controller_tip_path()
        ret = controller_maps[self.name][ctp]

        controller_args = self.get_controller_args(ret['argspec'])
        view, (model, _) = ret['app'](**controller_args)

        return model, view, controller_args

    def get_controller_args(self, argspec):
        """
        Given an argspec, return the controller args filled in with data from the
        invocation.
        """
        # dict of args that were defined in the controller tip with defaults
        # can be primitives, can be constants...
        kwargs = dict(zip(*[reversed(l) for l in (argspec.args, argspec.defaults or [])]))

        # list of args that do not contain primitives, these need to be replaced
        # data from the request.form / request.args / command line args / etc.
        args = [item for item in argspec.args if item not in kwargs.keys()]

        for item, value in kwargs.iteritems():
            if GiottoPrimitive in value.mro():
                kwargs[item] = self.get_primitive(value.__name__)

        for arg in args:
            kwargs[arg] = self.data(arg)

        return kwargs

    def output(self):
        pass