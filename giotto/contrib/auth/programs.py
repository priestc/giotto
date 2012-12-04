from giotto.programs import GiottoProgram
from giotto.views import BasicView
from giotto.primitives import LOGGED_IN_USER
from giotto.models import is_authenticated

from models import User
from views import BasicRegisterForm
from middleware import AuthenticationMiddleware, SetAuthenticationCookie, LogoutMiddleware

class UserRegistrationSubmit(GiottoProgram):
    name = 'register'
    controllers = ('http-post', 'cmd')
    model = [User.new_user, User(username='test', password='pass')]
    view = BasicRegisterForm

class UserRegistrationForm(GiottoProgram):
    name = 'register'
    controllers = ('http-get', )
    model = []
    view = BasicRegisterForm

class LoginForm(GiottoProgram):
    name = 'login'
    controllers = ('http-get', )
    model = []
    view = BasicRegisterForm

class LoginSubmit(GiottoProgram):
    """
    When the user submits the login form, the data get sent to this program.
    If their username/password match, the cookie is made and they are logged in.
    """
    name = 'login'
    controllers = ('http-post', )
    input_middleware = [AuthenticationMiddleware]
    model = [is_authenticated('Login credentials incorrect'), {'user': User('test', password='pass')}]
    view = BasicView
    output_middleware = [SetAuthenticationCookie]

class Logout(GiottoProgram):
    name = "logout"
    controllers = ('http-post', 'cmd')
    output_middleware = [LogoutMiddleware]

class ListAllUsers(GiottoProgram):
    name = 'all_users'
    controllers = ('http-get', 'cmd')
    model = [User.all]
    view = BasicView

manifest = ProgramManifest({
    'login': LoginSubmit(),
    'login_form': LoginForm(),
    'register': UserRegistrationSubmit(),
    'register_form': UserRegistrationForm(),
})

management_manifest = ProgramManifest({
    'list_all': ListAllUsers(),
})