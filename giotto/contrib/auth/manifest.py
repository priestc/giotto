from giotto import get_config
from giotto.programs import GiottoProgram, ProgramManifest
from giotto.views import GiottoView, BasicView, jinja_template
from giotto.control import Redirection

from .middleware import NotAuthenticatedOrRedirect, AuthenticationMiddleware, NotAuthenticatedOrDie, LogoutMiddleware
from .models import create_session, basic_register, User

def create_auth_manifest(**kwargs):
    """
    Creates a basic authentication manifest for logging in, logging out and
    registering new accounts.
    """
    class AuthProgram(GiottoProgram):
        pre_input_middleware = [AuthenticationMiddleware]

    def register(username, password, password2):
        """
        Decorated version of basic_register with a callback added.
        """
        result = basic_register(username, password, password2)
        callback = kwargs.pop('post_register_callback', None)
        if callback:
            session = get_config('session')
            user = session.query(User).filter_by(username=username).first()
            callback(user)
        return result

    return ProgramManifest({
        'login': [
            AuthProgram(
                """
                Prints out the HTML form for logging in.
                """,
                name="Login (form)",
                input_middleware=[NotAuthenticatedOrRedirect('/')],
                view=BasicView(
                    html=jinja_template('login.html'),
                ),
            ),
            AuthProgram(
                """
                Matches up the username/password against the database, and adds the auth cookies.
                """,
                name="Login (post)",
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
            """
            Send the user here to log them out. Removes their cookies and deletes the auth session.
            """,
            name="Logout",
            view=BasicView(
                html=Redirection('/'),
            ),
            output_middleware=[LogoutMiddleware],
        ),
        'register': [
            AuthProgram(
                """
                This program returns the HTML page with the form for registering a new account.
                HTTP-get only.
                """,
                name="Register (form)",
                input_middleware=[NotAuthenticatedOrRedirect('/')],
                view=BasicView(
                    html=jinja_template('register.html'),
                ),
            ),
            AuthProgram(
                """
                When you POST the register form, this program handles creating the new user, then redirecting you to '/'
                """,
                name="Register (post)",
                controllers=['http-post'],
                model=[register],
                view=BasicView(
                    html=lambda m: Redirection('/', persist={'giotto_session': m['session_key']}),
                ),
            ),
        ],
    })