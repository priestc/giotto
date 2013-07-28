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
            setattr(self, k, v)

    def __str__(self):
        return self.message

    def __setattr__(self, attr, value):
        """
        When setting values, make into a dictionary with 'message' and 'value'
        keys.
        """
        if attr == 'message':
            return super(InvalidInput, self).__setattr__(attr, value)
        if value is None:
            return super(InvalidInput, self).__setattr__(attr, None)
        if type(value) is not dict:
            value = {'value': value, 'message': ''}
            return super(InvalidInput, self).__setattr__(attr, value)
        if not 'message' in value:
            value['message'] = ''
        if not 'value' in value:
            value['value'] = ''

        super(InvalidInput, self).__setattr__(attr, value)

    def __getitem__(self, item):
        # be permissive of attribute errors because jinja templates
        # need to not blow up when there are no errors.
        if not item in self.__dict__:
            return Mock()

class InvalidInvocation(GiottoException):
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