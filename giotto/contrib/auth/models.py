import re
import bcrypt

from giotto.exceptions import InvalidInput
from giotto.utils import random_string
from giotto.primitives import LOGGED_IN_USER
from giotto import get_config
from giotto.models import User

def basic_register(username, password, password2):
    """
    Register a user and session, and then return the session_key and user.
    """
    if password != password2:
        raise InvalidInput(password={'message': "Passwords do not match"},
                           username={'value': username})
    user = User.objects.create_user(username, password)
    return create_session(user.username, password)

def create_session(username, password):
    """
    Create a session for the user, and then return the key.
    """
    user = User.objects.get_user_by_password(username, password)
    auth_session_engine = get_config('auth_session_engine')
    if not user:
        raise InvalidInput('Username or password incorrect')
    session_key = random_string(15)
    while auth_session_engine.get(session_key):
        session_key = random_string(15)
    auth_session_engine.set(session_key, user.username, get_config('auth_session_expire'))
    return {'session_key': session_key, 'user': user}