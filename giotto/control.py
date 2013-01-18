class GiottoControl(object):
    pass

class Redirection(GiottoControl):
    # because render functions have this defined, and this onject can be used in lieu
    # of a render function.
    __name__ = '__Redirection'
    def __init__(self, path, persist={}):
        self.path = path
        self.persist = persist