from giotto.views import GiottoView, renders
from giotto.control import Redirection

class BasicRegisterForm(GiottoView):
    @renders('text/html')
    def html(self, result):
        return """<!DOCTYPE html>
        <html>
            <body>
                <form method="post" action="">
                    username: <input name="username" type="text"><br>
                    password: <input name="password" type="password"><br>
                    <input type="submit">
                </form>
            </body>
        </html>
        """

def LoginView(http_redirect=None):
    """
    After logging in, redirect the user to the ``http_redirect`` program.
    This is a meta program, a function that returns a program.
    ``http_redirect`` can be either a string, or a three item tuple with M objects:
    http_redirect=('/blog', [m.id], {}) | http_redirect=('/blog', [], {'name': M['name']})
    """
    class LoginView(GiottoView):
        """
        ``result`` is the session that was newly created. consult the
        ``create_session`` model for reference.
        """
        @renders('text/html')
        def html(self, result):
            ty = type(http_redirect)
            if ty == list or ty == tuple:
                assert len(http_redirect) == 3, "http_redirect must be three items"
                return Redirection(http_redirect[0], args=http_redirect[1], kwargs=http_redirect[2])
            else:
                # assume a string was passed in.
                return Redirection(http_redirect)
    return LoginView