from collections import defaultdict
from giotto.utils import Mock

class GiottoException(Exception):
    """
    Represents an exception that Giotto catches internally.
    """

class InvalidInput(GiottoException):
    def __init__(self, message=None, data=None):
        if not data:
            self.__dict__ = defaultdict(lambda: '', {'message': message})
        else:
            self.__dict__ = defaultdict(lambda: '', data)

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