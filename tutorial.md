First, install giotto:

    $ pip install giotto

Now create a controller file:

    $ giotto_controller --http-dev --cmd --demo

This will create a "controller file" which will act as a gateway between your
application and the outside world. The file generated will be called 'giotto'

The `--http-dev` and `--cmd` flags tells giotto to include the plumbing for those
two "controller classes" into the controller file. Your application can now be
interacted with from the command line or through HTTP dev server. If you only
want to interact with you app through the commandline, then you could leave off
the `--http-dev`. The option `--demo` tells giotto to include a simple "multiply"
model/view combo to demonstrate how giotto works.

Inside the `giotto` file, you will see the following (plus some extra plumbing 
at the bottom):

    class ColoredMultiplyView(GiottoTemplateView):
        def text_plain(self, result):
            {% raw %}return "{{ obj.x }} * {{ obj.y }} == {{ obj.product }}"{% endraw %}

        def application_json(self, result):
            import json
            return json.dumps(result)

        def text_html(self, result):
            return """<!DOCTYPE html>
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"></script>
            <html>
                <body>
                    {% raw %}<span style="color: blue">{{ obj.x }} * {{ obj.y }}</span> == 
                    <span style="color: red">{{ obj.product }}</span>{% endraw %}
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
        model = [multiply]
        view = [ColoredMultiplyView]


The first class, theone that inherits from `GiottoTemplateView` is the view,
the function `multiply` is the model, and the last class (the one that subclasses
`GiottoProgram`) is called the "program", which binds a group of controllers
to a model and view. Each program contains a controller, a model
(optional) and a view. You can also add middleware and cache, but we'll deal
with those later.

To see our example multiply program in action, run the http-dev serve by running
the following command:

    $ giotto http-dev

This will run the development server (you must have werkzeug installed). Now
lets take a look at the `multiply` program. Point your browser to:
http://localhost:5000/multiply?x=4&y=8

The browser should now be displaying `4 * 8 == 32`. With the part before the `==`
in blue, and the part after in red.

Now, open up your browser's javascript console (firebug if you're a firefox user).
Type in the following:

    $.ajax({url: window.location.href, success: function(a) {console.log(a)}})

You should see a json representation of the page. The HTTP controller automatically
changes the return mimetype to "application/json" when the request comes from
ajax.

Lets take a look at this program as viewed from the commandline. Press `ctrl+c`
to stop the dev server.

Form the shell, run the following command:

    $ giotto multiply --x=4 --y=8

The output should be exactly the same. It should say `4 * 8 == 32` with the `32`
in red and the `4 * 8` in blue. The model that is being called
here is exactly the same as we saw being called from the browser. The only
difference is the way the result is visualized, and the way data moves between the
user and the computer.

