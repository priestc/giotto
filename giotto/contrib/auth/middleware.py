from .models import User
from giotto.exceptions import NotAuthorized
from giotto.control import Redirection

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

        username = request.cookies.get('username', None)
        hash_ = request.cookies.get('password', None)

        if username and hash_:
            user = User.get_user_by_hash(username, hash_)

        setattr(request, 'user', user)
        return request

    def cmd(self, request):
        user = None
        u = request.args('username', None)
        p = request.args('password', None)
        user = User.get_user_by_password(u, p) if u and p else None

        setattr(request, 'user', user)
        return request


class SetAuthenticationCookies(object):
    """
    Place this middleware class in the output stream to set the cookies that
    are used to authenticate each subsequent request.
    """
    def http(self, request, response):
        if hasattr(request, 'user') and request.user:
            response.set_cookie('username', request.user.username)
            response.set_cookie('password', request.user.password)
        elif 'password' in request.form and 'password' in request.form:
            # user just registered.
            username = request.form['username']
            password = request.form['password']
            user = User.get_user_by_password(username, password)
            response.set_cookie('username', user.username)
            response.set_cookie('password', user.password)

        return response

    def cmd(self, request, response):
        if request.user:
            request.environment['giotto_username'] = request.username
            request.environment['giotto_password'] = request.password
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
        response.delete_cookie('username')
        response.delete_cookie('password')
        return response