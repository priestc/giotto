from giotto.programs import GiottoProgram, ProgramManifest
from giotto.views import GiottoView, BasicView, jinja_template
from giotto.control import Redirection

from .middleware import NotAuthenticatedOrRedirect, AuthenticationMiddleware, NotAuthenticatedOrDie, LogoutMiddleware
from .models import create_session, basic_register

def create_auth_manifest(*args):
    """
    Creates a basic authentication manifest for logging in, logging out and
    registering new accounts.
    """

    class AuthProgram(GiottoProgram):
        pre_input_middleware = [AuthenticationMiddleware]
    return ProgramManifest({
        'login': [
            AuthProgram(
                input_middleware=[NotAuthenticatedOrRedirect('/')],
                view=BasicView(
                    html=jinja_template('login.html'),
                ),
            ),
            AuthProgram(
                input_middleware=[NotAuthenticatedOrDie],
                controllers=['http-post', 'cmd'],
                model=[create_session, {'username': 'mock_user', 'session_key': 'XXXXXXXXXXXXXXX'}],
                view=BasicView(
                    persist=lambda m: {'giotto_session': m['session_key']},
                    html=lambda m: Redirection('/'),
                ),
            ),
        ],
        'logout': AuthProgram(
            view=BasicView(
                html=Redirection('/'),
            ),
            output_middleware=[LogoutMiddleware],
        ),
        'register': [
            AuthProgram(
                input_middleware=[NotAuthenticatedOrRedirect('/')],
                view=BasicView(
                    html=jinja_template('register.html'),
                ),
            ),
            AuthProgram(
                controllers=['http-post'],
                model=[basic_register],
                view=BasicView(
                    html=lambda m: Redirection('/', persist={'giotto_session': m['session_key']}),
                ),
            ),
        ],
    })