from giotto.views import GiottoView

class BasicRegisterForm(GiottoView):
    def text_html(self, result):
        return """<html><body>
        <form method="post" action="#">
            username <input name="username"><br>
            password <input name="password"><br>
            <input type="submit">
        </form>
        </body></html>
        """