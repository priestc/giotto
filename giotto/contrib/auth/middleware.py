from __future__ import print_function
import json
import getpass

from .models import User
from giotto.exceptions import NotAuthorized
from giotto.control import Redirection
from giotto import get_config
from giotto.middleware import GiottoOutputMiddleware, GiottoInputMiddleware

class AuthenticationMiddleware(GiottoInputMiddleware):
    """
    This input middleware class must preceed any other authentication middleware class.
    It is used to extract authentiction information from the request, and
    verify that the credientials are correct.
    """
    def http(self, request):
        user = None
        session_key = request.cookies.get('giotto_session', None)
        if not session_key and request.POST:
            session_key = request.POST.get('auth_session', None)
        if session_key:
            username = get_config('auth_session').get(session_key)
            user = get_config('session').query(User).filter_by(username=username).first()

        setattr(request, 'user', user)
        return request

    def cmd(self, request):
        user = None
        session_key = request.enviornment.get('GIOTTO_SESSION', None)
        if session_key:
            user = get_config('auth_session').get(session_key)

        if not user:
            print("Username:")
            username = raw_input()
            password = getpass.getpass()
            user = User.get_user_by_password(username, password)

        setattr(request, 'user', user)
        return request

class AuthenticatedOrDie(GiottoInputMiddleware):
    """
    Put this in the input middleware stream to fail any requests that aren't
    made by authenticated users
    """
    def http(self, request):
        if not request.user:
            raise NotAuthorized('Must be Logged in for this program')
        return request

    def cmd(self, request):
        user = getattr(request, 'user', None)
        if not user:
            raise SystemExit("Must be logged in")
        return request

class NotAuthenticatedOrDie(GiottoInputMiddleware):
    """
    Put this in the input middleware stream to fail any requests that aren't
    made by authenticated users
    """
    def http(self, request):
        if request.user:
            raise NotAuthorized('Must not be Logged in for this program')
        return request

    def cmd(self, request):
        user = getattr(request, 'user', None)
        if user:
            raise SystemExit("Must not be logged in for this program")
        return request

def AuthenticatedOrRedirect(invocation):
    """
    Middleware class factory that redirects if the user is not logged in.
    Otherwise, nothing is effected.
    """
    class AuthenticatedOrRedirect(GiottoInputMiddleware):
        def http(self, request):
            if request.user:
                return request
            return Redirection(invocation)

        def cmd(self, request):
            if request.user:
                return request
            return Redirection(invocation)

    return AuthenticatedOrRedirect


def NotAuthenticatedOrRedirect(invocation):
    """
    Middleware class factory that redirects if the user is not logged in.
    Otherwise, nothing is effected.
    """
    class NotAuthenticatedOrRedirect(GiottoInputMiddleware):
        def http(self, request):
            if not request.user:
                return request
            return Redirection(invocation)

        def cmd(self, request):
            if not request.user:
                return request
            return Redirection(invocation)

    return NotAuthenticatedOrRedirect


class LogoutMiddleware(GiottoOutputMiddleware):
    """
    Logout the user. This not only deletes the session key in persistence (the
    cookie), but also nukes the session in the database so it will never
    ve valid again.
    """
    def http(self, request, response):
        if request.method == 'POST' and 'auth_session' in request.POST:
            key = request.POST['auth_session']
            session_key = get_config('auth_session').set(key, None, 1) # nuke session
        response.delete_cookie('giotto_session')
        return response