demo_application = '''from giotto.programs import GiottoProgram, ProgramManifest
from giotto.views import BasicView, renders

class ColoredMultiplyView(BasicView):
    @renders('text/plain')
    def plaintext(self, result):
        return "{{ obj.x }} * {{ obj.y }} == {{ obj.product }}"

    @renders('text/html')
    def html(self, result):
        return """<!DOCTYPE html>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"></script>
        <html>
            <body>
                <span style="color: blue">%(x)s * %(y)s</span> == 
                <span style="color: red">%(product)s</span>
            </body>
        </html>""" % result

    @renders('text/x-cmd')
    def cmd(self, result):
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

    @renders('text/x-irc')
    def irc(self, result):
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

manifest = ProgramManifest({
    'multiply': GiottoProgram(
        controllers = ('http-get', 'cmd', 'irc'),
        model=[multiply, {'x': 3, 'y': 3, 'product': 9}],
        view=ColoredMultiplyView
    )
})'''