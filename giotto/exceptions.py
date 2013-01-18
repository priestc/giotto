from collections import defaultdict
from giotto.utils import Mock

class GiottoException(Exception):
    """
    Represents an exception that Giotto catches internally.
    """

class InvalidInput(GiottoException):
    def __init__(self, message='', **kwargs):
        self.message = message
        for k, v in kwargs.items():
            setattr(self, k, {})
            if type(v) is dict:
                if not 'message' in v:
                    getattr(self, k)['message'] = ''
                else:
                    getattr(self, k)['message'] = v['message']
                if not 'value' in v:
                    getattr(self, k)['value'] = ''
                else:
                    getattr(self, k)['value'] = v['value']
            else:
                getattr(self, k)['message'] = ''
                getattr(self, k)['value'] = v

    def __str__(self):
        return self.message

    def __getitem__(self, item):
        # be permissive of attribute errors because jinja templates
        # need to not blow up when there are no errors.
        if not item in self.__dict__:
            return Mock()

class InvalidProgram(GiottoException):
    pass

class ProgramNotFound(GiottoException):
    pass

class DataNotFound(GiottoException):
    pass

class NoViewMethod(GiottoException):
    pass

class MockNotFound(GiottoException):
    pass

class NotAuthorized(GiottoException):
    pass

class ControlMiddlewareInterrupt(GiottoException):
    def __init__(self, message=None, control=None):
        self.control = control
        self.message = message

        # render the control object now because this object will never
        self.control.render(None, 'some_mimetype', None)