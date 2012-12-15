.. _ref-authentication:

==============
Authentication
==============

There is an application within the contrib submodule called ``auth`` that handles authentication.
This application uses SQLAlchemy_ to store user data.

This ``User`` model stores two pieces of information: username and password.
The password is stored as an encrypted string.
Encrypting is done automatically by the bcrypt_ library.

This user class is not intended to store all information that an application developer would want to store for a user.
The developer is meant to create their own user profile table that connects to the User table via foreign key.

Enabling Authentication for your application
============================================

An authenticated application typically contans three parts:

1. A registration page.
2. A login page.
3. A log out page.
4. Some way to authenticate requests so other parts of the application can utilize authentication.

Login page
==========

To set up a login page, add the following to your project's manifest::

    from giotto.contrib.auth.models import is_authenticated
    from giotto.contrib.auth.middleware import SetAuthenticationCookies
    from giotto.control import Redirection
    from giotto.programs import GiottoProgram
    from giotto.views import JinjaTemplateView

    {
        'login': [
            GiottoProgram(
                input_middleware=[AuthenticationMiddleware, NotAuthenticatedOrRedirect('/')],
                controllers=('http-get',),
                view=JinjaTemplateView('login.html'),
            ),
            GiottoProgram(
                controllers=('http-post',),
                input_middleware=[AuthenticationMiddleware],
                model=[is_authenticated("Invalid username or password")],
                view=Redirection('/'),
                output_middleware=[SetAuthenticationCookies],
            ),
        ],
    }

The first program handles generating the login form.
The second program handles the submitted data from the login form.
You may want to change the name of the template that is passed into the first program.
The login template must contain a form that POSTS's its data to a page of the same name of the form.
The name of the programs (``login`` in this example) can be anything.
You can also change the path that the second program redirects to after successful registration.
In this case, on successful registration, the user is redirected to the root program: ``/``.

The login template should look a little like this::

    <!DOCTYPE html>
    <html>
        <body>
            <h1>Login</h1>
            {% if errors %}
                <span style="color: red">{{ errors.message }}</span>
            {% endif %}
            <form method="post">
                username: <input type="text" name="username">
                <br>
                password: <input type="password" name="password">
                <br>
                <input type="submit">
            </form>
        </body>
    </html>

The value of ``{{ errors }}`` will be empty when the login form is first rendered.
If the data that is submitted is not valid (it does not match an existing user/pasword),
the form is re-generated with the ``errors`` object containing error information.

Register page
=============

To add a registration page to your application, add the following to your manifest::

    from giotto.contrib.auth.models import basic_register
    from giotto.contrib.auth.middleware import SetAuthenticationCookies
    from giotto.control import Redirection
    from giotto.programs import GiottoProgram
    from giotto.views import JinjaTemplateView

    {
        'register': [
            GiottoProgram(
                controllers=('http-get',),
                view=JinjaTemplateView('register.html'),
            ),
            GiottoProgram(
                controllers=('http-post',),
                model=[basic_register],
                view=Redirection('/'),
                output_middleware=[SetAuthenticationCookies],
            ),
        ],
    }

The register template should look like this::

    <!DOCTYPE html>
    <html>
        <body>
            <h1>Register</h1>
            {% if errors %}
                <span style="color: red">{{ errors.message }}</span>
            {% endif %}
            <form method="post">
                <span style="color: red">{{ errors.username.message }}</span><br>
                username: <input type="text" name="username" value="{{ errors.username.value }}">
                <br>
                <span style="color: red">{{ errors.password.message }}</span><br>
                password: <input type="password" name="password">
                password again: <input type="password" name="password2">
                <br>
                <input type="submit">
            </form>
        </body>
    </html>

The value of the ``errors`` object will have a ``password`` and ``username`` object,
which will each contain ``message`` and ``value`` keys.
``message`` contains the error message, and ``value`` contain the previous value that was entered.


Logout Page
===========

Adding a logout program is very simple, just add this to your project's manifest::

    from giotto.programs import GiottoProgram
    from giotto.control import Redirection
    from giotto.contrib.auth.middleware import LogoutMiddleware

    {
        'logout': GiottoProgram(
            view=Redirection('/'),
            output_middleware=[LogoutMiddleware],
        ),
    }

You can change the url that you get redirected to after logging out by changing the value passed into ``Redirection``.

Interacting with authentication with other programs
===================================================

To access the currently logged in user from within a model function,
add the ``LOGGED_IN_USER`` primitive to your model function's arguments::

    from giotto.primitives import LOGGED_IN_USER
    from giotto.programs import GiottoProgram, ProgramManifest
    from giotto.contrib.auth.middleware import AuthenticationMiddleware
    from giotto.views import BasicView

    def show_logged_in_user(user=LOGGED_IN_USER):
        return {'user': user}

    manifest = ProgramManifest({
        'show_logged_in': GiottoProgram(
            input_middleware=[AuthenticationMiddleware],
            model=[show_logged_in_user],
            view=BasicView,
        )
    })

The controller knows how to extract ``LOGGED_IN_USER`` from the incoming request.
This primitive can only be used if the ``AuthenticationMiddleware`` is added to the input middleware stream.
All programs that wish to take advantage of the authentication system need to have ``AuthenticationMiddleware`` added.
It may be convenient to create a subclass of ``GiottoProgram`` with ``AuthenticationMiddleware`` baked in::

    from giotto.programs import GiottoProgram, ProgramManifest
    from giotto.contrib.auth.middleware import AuthenticationMiddleware
    from giotto.views import BasicView

    class AuthProgram(GiottoProgram):
        input_middleware=[AuthenticationMiddleware]

    def show_logged_in_user(user=LOGGED_IN_USER):
        return {'user': user}

     manifest = ProgramManifest({
        'show_logged_in': AuthProgram(
            model=[show_logged_in_user],
            view=BasicView,
        )
    })

You can also take advantage of a few middleware classes::

AuthenticatedOrRedirect and NotAuthenticatedOrRedirect
------------------------------------------------------

These middleware classes, if added to the input middleware stream,
will redirect the request to another program (via 302 redirect) depending on authentication status::

    from giotto.programs import GiottoProgram
    from giotto.contrib.auth.middleware import AuthenticationMiddleware, NotAuthenticatedOrRedirect
    from giotto.views import JinjaTemplateView

    GiottoProgram(
        input_middleware=[AuthenticationMiddleware, NotAuthenticatedOrRedirect('/')],
        controllers=('http-get',),
        view=JinjaTemplateView('login.html'),
    ),

In this example, only non authenticated users will see the ``login.html`` page.
All authenticated users will get redirected to the root program.

AuthenticatedOrDie
------------------

This middleware class will return a 403 (error page) if the request is not authenticated::

    from giotto.programs import GiottoProgram
    from giotto.contrib.auth.middleware import AuthenticationMiddleware, AuthenticatedOrDie
    from giotto.views import JinjaTemplateView

    {
        'new': GiottoProgram(
            input_middleware=[AuthenticationMiddleware, AuthenticatedOrDie],
            view=JinjaTemplateView('new_blog.html'),
            controllers=('http-get',),
        ),
    }

In this example, only authenticated users can create a new blog. All other users will get a 403 page.

.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _bcrypt: http://www.mindrot.org/projects/py-bcrypt/