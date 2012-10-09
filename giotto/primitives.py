class GiottoPrimitive(object): 
    def __init__(self, name):
        self.name = name

LOGGED_IN_USER = GiottoPrimitive("LOGGED_IN_USER")
RAW_PAYLOAD = GiottoPrimitive("RAW_PAYLOAD")
USER_COUNTRY = GiottoPrimitive("USER_COUNTRY")
PREVIOUS_INPUT = GiottoPrimitive("PREVIOUS_INPUT")
PREVIOUS_ERRORS = GiottoPrimitive("PREVIOUS_ERRORS")