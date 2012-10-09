class GiottoProgram(object):
    input_middleware = []
    name = None
    controller = None
    cache = 0
    model = (None, )
    view = None
    output_middleware = []

class GiottoAbstractProgram(GiottoProgram):
    pass