from .models import User
from giotto.exceptions import NotAuthorized
from giotto.control import Redirection
from giotto import config
from giotto.utils import random_string

class AuthenticationMiddleware(object):
    """
    This input middleware class must preceed any other authentication middleware class.
    It is used to extract authentiction information from the request, and
    verify that the credientials are correct.
    """
    def http(self, request):
        user = None
        if request.method == 'POST':
            u = request.form.get('username', None)
            p = request.form.get('password', None)
            user = User.get_user_by_password(u, p) if u and p else None

        session_key = request.cookies.get('giotto_session', None)
        if session_key:
            username = config.auth_session.get(session_key)
            user = config.session.query(User).filter_by(username=username).first()

        setattr(request, 'user', user)
        return request

    def cmd(self, request):
        return request


class SetAuthenticationCookies(object):
    """
    Place this middleware class in the output stream to set the cookies that
    are used to authenticate each subsequent request.
    """

    def make_session(self, user):
        """
        Create a session for the user, and then return the key.
        """
        session_key = random_string(15)
        while config.auth_session.get(session_key):
            session_key = random_string(15)
        config.auth_session.set(session_key, user.username, config.auth_session_expire)
        return session_key

    def http(self, request, response):
        if hasattr(request, 'user') and request.user:
            username = request.user.username
            password = request.user.password
            user = User.get_user_by_hash(username, password)
        elif 'password' in request.form and 'password' in request.form:
            # user just registered.
            username = request.form['username']
            password = request.form['password']
            user = User.get_user_by_password(username, password)
        
        if not user:
            return response

        session_key = self.make_session(user)
        response.set_cookie('giotto_session', session_key)

        return response

    def cmd(self, request, response):
        return response


class AuthenticatedOrDie(object):
    """
    Put this in the input middleware stream to fail any requests that aren't
    made by authenticated users
    """
    def http(self, request):
        if not request.user:
            raise NotAuthorized('Must be Logged in for this program')
        return request


def AuthenticatedOrRedirect(invocation, args=[], kwargs={}):
    """
    Middleware class factory that redirects if the user is not logged in.
    Otherwise, nothing is effected.
    """
    class AuthenticatedOrRedirect(object):
        def http(self, request):
            if request.user:
                return request
            return Redirection(invocation, args, kwargs)
    return AuthenticatedOrRedirect


def NotAuthenticatedOrRedirect(invocation, args=[], kwargs={}):
    """
    Middleware class factory that redirects if the user is not logged in.
    Otherwise, nothing is effected.
    """
    class NotAuthenticatedOrRedirect(object):
        def http(self, request):
            if not request.user:
                return request
            return Redirection(invocation, args, kwargs)
    return NotAuthenticatedOrRedirect


class LogoutMiddleware(object):
    def http(self, request, response):
        response.delete_cookie('giotto_session')
        return response