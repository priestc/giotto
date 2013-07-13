class GiottoPrimitive(object): 
    def __init__(self, name):
        self.name = name

    def __repr__(self):
    	return "(Giotto Primitive: %s)" % self.name

LOGGED_IN_USER = GiottoPrimitive("LOGGED_IN_USER")
ALL_DATA = GiottoPrimitive("ALL_DATA")
USER_COUNTRY = GiottoPrimitive("USER_COUNTRY")
PREVIOUS_INPUT = GiottoPrimitive("PREVIOUS_INPUT")
PREVIOUS_ERRORS = GiottoPrimitive("PREVIOUS_ERRORS")
ALL_PROGRAMS = GiottoPrimitive('ALL_PROGRAMS')
USER = GiottoPrimitive("USER")
RAW_INVOCATION_ARGS = GiottoPrimitive("RAW_INVOCATION_ARGS")