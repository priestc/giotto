from collections import defaultdict
from giotto.utils import Mock

class InvalidInput(Exception):
    def __init__(self, message=None, data=None):
        if not data:
            self.__dict__ = defaultdict(lambda: '', {'message': message})
        else:
            self.__dict__ = defaultdict(lambda: '', data)

    def __getitem__(self, item):
        if not item in self.__dict__:
            return Mock()

class InvalidProgram(Exception):
    pass

class ProgramNotFound(Exception):
    pass

class DataNotFound(Exception):
    pass

class NoViewMethod(Exception):
    pass

class MockNotFound(Exception):
    pass

class NotAuthorized(Exception):
    pass

class ControlMiddlewareInterrupt(Exception):
    def __init__(self, message=None, control=None):
        self.control = control
        self.message = message

        # render the control object now because this object will never
        self.control(None).render('some_mimetype')