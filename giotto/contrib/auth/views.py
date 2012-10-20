from giotto.views import GiottoView

class BasicRegisterForm(GiottoView):
    def text_html(self, result):
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