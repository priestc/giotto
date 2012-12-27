import re
import bcrypt

from giotto.exceptions import InvalidInput
from giotto.utils import random_string
from giotto.primitives import LOGGED_IN_USER
from giotto import config

from sqlalchemy import Column, String

class User(config.Base):
    username = Column(String, primary_key=True)
    password = Column(String)

    def __init__(self, username, password):
        self.username = username
        hashed = ''
        if not password == '':
            # skip hashing process if the password field is left blank
            # helpful for creating mock user objects without slowing things down.
            hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        self.password = hashed
        self.raw_password = password
    
    def validate(self):
        """
        Make sure this newly created user instance meets the username/password
        requirements
        """
        r = getattr(config, 'auth_regex', r'^[\d\w]{4,30}$')
        errors = {}
        if not re.match(r, self.username):
            errors['username'] = {'message': 'Username not valid', 'value': self.username}
        if len(self.raw_password) < 4:
            errors['password'] = {'message': 'Password much be at least 4 characters'}
        if config.session.query(User).filter_by(username=self.username).first():
            errors['username'] = {'message': 'Username already exists', 'value': self.username}

        if errors:
            raise InvalidInput("User data not valid", **errors)

    @classmethod
    def get_user_by_password(cls, username, password):
        """
        Given a username and a raw, unhashed password, get the corresponding
        user, retuns None if no match is found.
        """
        user = config.session.query(cls).filter_by(username=username).first()

        if not user:
            return None

        if bcrypt.hashpw(password, user.password) == user.password:
            return user
        else:
            return None

    @classmethod
    def get_user_by_hash(cls, username, hash_):
        return config.session.query(cls)\
                     .filter_by(username=username, password=hash_)\
                     .first()

    @classmethod
    def create(cls, username, password):
        """
        Create a new user instance
        """
        user = cls(username=username, password=password)
        user.validate()
        config.session.add(user)
        config.session.commit()
        return user

    @classmethod
    def all(cls):
        return config.session.query(cls).all()

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.username, self.password)

def is_authenticated(message):
    """
    Is this request coming from a user who is logged in? This is a meta function.
    When adding this to a program, call it with the mesage you want to be displayed
    when no user is found.
    """
    def inner(user=LOGGED_IN_USER):
        if not user:
            raise InvalidInput(message)
        return {'user', user}
    return inner

def basic_register(username, password, password2):
    """
    Register a user and session, and then return the session_key and user.
    """
    if password != password2:
        raise InvalidInput(data={'password': {'message': "Passwords do not match"},
                                 'username': {'value': username}})
    user = User.create(username, password)
    return create_session(user)

def create_session(user=LOGGED_IN_USER):
    """
    Create a session for the user, and then return the key.
    """
    if not user:
        raise InvalidInput('Username or password incorrect')
    session_key = random_string(15)
    while config.auth_session.get(session_key):
        session_key = random_string(15)
    config.auth_session.set(session_key, user.username, config.auth_session_expire)
    return {'session_key': session_key, 'user': user}