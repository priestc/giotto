demo_application = '''from giotto.programs import GiottoProgram
from giotto.views import GiottoTemplateView

class ColoredMultiplyView(GiottoTemplateView):
    def text_plain(self, result):
        return "{{ obj.x }} * {{ obj.y }} == {{ obj.product }}"

    def application_json(self, result):
        import json
        return json.dumps(result)

    def text_html(self, result):
        return """<!DOCTYPE html>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"></script>
        <html>
            <body>
                <span style="color: blue">{{ obj.x }} * {{ obj.y }}</span> == 
                <span style="color: red">{{ obj.product }}</span>
            </body>
        </html>"""

    def text_cmd(self, result):
        from colorama import init, Fore
        init()
        return "{blue}{x} * {y}{reset} == {red}{product}{reset}".format(
            blue=Fore.BLUE,
            red=Fore.RED,
            reset=Fore.RESET,
            x=result['x'],
            y=result['y'],
            product=result['product'],
        )

    def text_irc(self, result):
        return "{blue}{x} * {y}{reset} == {red}{product}{reset}".format(
            blue="\x0302",
            red="\x0304",
            reset="\x03",
            x=result['x'],
            y=result['y'],
            product=result['product'],
        )


def multiply(x, y):
    return {'x': int(x), 'y': int(y), 'product': int(x) * int(y)}


class Multiply(GiottoProgram):
    name = "multiply"
    controllers = ('http-get', 'cmd', 'irc')
    model = [multiply, {'x': 3, 'y': 3, 'product': 9}]
    cache = None
    view = ColoredMultiplyView'''
