from .models import User

class AuthenticateMiddleware(object):
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


class SetAuthenticationCookie(object):
    def http(self, request, response):
        if request.user:
            response.set_cookie('username', request.user.username)
            response.set_cookie('password', request.user.password)
        return response

    def cmd(self, request, response):
        if request.user:
            request.environment['giotto_username'] = request.username
            request.environment['giotto_password'] = request.password
        return response