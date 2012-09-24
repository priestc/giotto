import redis
import bcrypt

from giotto.core import config

def get_user(username):
    """
    Given a username, return the associated user
    """
    r = redis.Redis(config.redis_host)
    user = r.get(username)
    return user

def new_user(username, password):
    """
    Create a new user instance. Passed in is the password of this user
    """
    pass_hash = bcrypt # FIXME
    r = redis.Redis(config.redis_host)
    r.set(username, pass_hash)
    return user

def login(username, password):
    r = redis.Redis(config.redis_host)
    pass_hash = r.get(username)
    return pass_hash == hash(password)

class AuthInputMiddleware(object):
    def http(request):
        pass_hash = request.cookie.get('pass_hash', None)
        username = request.cookie.get('username', None)
        if not username or not pass_hash:
            return request
        request.authenticated = login(username, pass_hash)
        return request