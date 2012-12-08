import re
import bcrypt

from giotto.exceptions import InvalidInput
from giotto import config

from sqlalchemy import Column, String

class User(config.Base):
    username = Column(String, primary_key=True)
    password = Column(String)

    def __init__(self, username, password):
        self.username = username
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        self.password = hashed
        self.raw_password = password
    
    def validate(self):
        """
        Make sure this newly created user instance meets the username/password
        requirements
        """
        r = getattr(config, 'auth_regex', r'^[\d\w]{4,30}$')
        if not re.match(r, self.username):
            raise InvalidInput('Username not valid')
        if len(self.raw_password) < 4:
            raise InvalidInput('Password much be at least 4 characters')
        if config.session.query(User).filter_by(username=self.username).first():
            raise InvalidInput('Username already exists')

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
                      .filter_by(username=username, password=hash_).first()

    @classmethod
    def new_user(cls, username, password):
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
