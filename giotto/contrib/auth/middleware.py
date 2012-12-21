from .models import User
import json
from giotto.exceptions import NotAuthorized
from giotto.control import Redirection
from giotto import config
from giotto.middleware import GiottoOutputMiddleware, GiottoInputMiddleware

class AuthenticationMiddleware(GiottoInputMiddleware):
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
        
        if not user:
            session_key = request.cookies.get('giotto_session', None)
            if not session_key and request.form:
                session_key = request.form.get('auth_session', None)
            if session_key:
                username = config.auth_session.get(session_key)
                user = config.session.query(User).filter_by(username=username).first()

        setattr(request, 'user', user)
        return request

    def cmd(self, request):
        return request


class PresentAuthenticationCredentials(GiottoOutputMiddleware):
    """
    Place this middleware class in the output stream to set the cookies that
    are used to authenticate each subsequent request.
    """

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

        if 'json' in self.controller.mimetype:
            if not user:
                response.data = 'Not Authenticated'
                response.status_code = 401
                return response

            session_key = self.make_session(user)

            try:
                data = json.loads(response.data)
            except ValueError:
                # in the case of a redirect, the response data will be junk html
                # so it should be OK if we overwrite it.
                data = {}
            data['auth_session'] = session_key
            response.data = json.dumps(data)
        else:
            if not user:
                return response
            session_key = self.make_session(user)
            response.set_cookie('giotto_session', session_key)

        return response

    def cmd(self, request, response):
        return response


class AuthenticatedOrDie(GiottoInputMiddleware):
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
    class AuthenticatedOrRedirect(GiottoInputMiddleware):
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
    class NotAuthenticatedOrRedirect(GiottoInputMiddleware):
        def http(self, request):
            if not request.user:
                return request
            return Redirection(invocation, args, kwargs)
    return NotAuthenticatedOrRedirect


class LogoutMiddleware(GiottoOutputMiddleware):
    """
    Logout the user. This not only deletes the session key in persistence (the
    cookie), but also nukes the session in the database so it will never
    ve valid again.
    """
    def http(self, request, response):
        if request.method == 'POST' and 'auth_session' in request.form:
            key = request.form['auth_session']
            session_key = config.auth_session.set(key, None, 1) # nuke session
        response.delete_cookie('giotto_session')
        return response