from giotto.primitives import LOGGED_IN_USER
from giotto.exceptions import InvalidInput
from giotto.utils import get_config

def make_tables():
    config = get_config()
    Base = get_config().Base
    engine = get_config().engine
    Base.metadata.create_all(engine)
    return {'message': 'All tables created'}

def is_authenticated(user=LOGGED_IN_USER):
    if not user:
        raise InvalidInput("No user")
    return {'user', user}