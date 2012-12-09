class InvalidInput(Exception):
    def __init__(self, data):
        self.__dict__ = data

class InvalidProgram(Exception):
    pass

class ProgramNotFound(Exception):
    pass

class NoViewMethod(Exception):
    pass

class MockNotFound(Exception):
    pass

class NotAuthorized(Exception):
    pass