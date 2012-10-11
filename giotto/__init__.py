class GiottoProgram(object):
    input_middleware = []
    name = None
    controller = None
    cache = 0
    model = (None, )
    view = None
    output_middleware = []

    @classmethod
    def is_match(cls, controller, name):
        """
        Does this program match the current invocation prameters? 
        """
        return cls.name == name and controller in cls.controllers