class GiottoControl(object):
    pass


class Redirection(GiottoControl):
    def __init__(self, path, persist={}):
        self.path = path
        self.persist = persist