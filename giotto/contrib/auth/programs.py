from giotto.programs import GiottoProgram
from giotto.views import BasicView
from giotto.primitives import LOGGED_IN_USER
from giotto.models import is_authenticated

from models import User
from views import BasicRegisterForm
from middleware import AuthenticationMiddleware, SetAuthenticationCookie

class NewUserRegistration(GiottoProgram):
    name = 'register'
    controllers = ('http-post', 'cmd')
    model = [User.new_user, User(username='test', password='pass')]
    view = BasicRegisterForm

class NewUserRegistrationForm(GiottoProgram):
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
    model = [is_authenticated, {'user', User('test', password='pass')}]
    view = BasicView
    output_middleware = [SetAuthenticationCookie]