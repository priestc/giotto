.. _ref-tutorial:

===========================
Getting Started with Giotto
===========================

First, install giotto::

    $ pip install giotto

You can also get the latest version from the github::

    $ pip install git+git://github.com/priestc/giotto.git

Now create a new directory::

    $ mkdir demo

and inside that directory, run this command::

    $ cd demo
    $ giotto_project --http --cmd --demo

This will create a ``programs.py`` file, which contains your program objects.
It will also create a series of "concrete controller files",
which will act as a gateway between your application and the outside world.
The concrete controller files will be called ``giotto-http`` and ``giotto-cmd``

If you only want to interact with you application through the command line,
then you could leave off the ``--http`` flag when calling ``giotto_project`` (and vice versa).
The option ``--demo`` tells giotto to include a simple "multiply" program to demonstrate how giotto works.

Inside the ``programs.py`` file, you will see the following::

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
        view = ColoredMultiplyView

All Giotto applications are made up a collection of Giotto Programs. Each program class
defines a model, a view, and a set of controllers.

A "Giotto application" is the overall project,
such as a blog application, a content management system, or a twitter clone.
A "Giotto Program" is a "page" within an application.
An example of a program is "create blog", "view tweet" or "register user".

A Giotto program is made up of (at minimum) a model, a view, and a set of controllers.
In the above example, our application only contains one program called "mutiply".
All it does is take two numbers, and multiply them together.

To see our example ``multiply`` program in action,
start up the development server by running the following command::

    $ giotto-http --run

This will run the development server (you must have werkzeug installed).
Point your browser to: http://localhost:5000/multiply?x=4&y=8

The browser should now be displaying `4 * 8 == 32`. With the part before the `==`
in blue, and the part after in red.

The following order of events are occurring:

#. You make a web request to the development server that is hooked up to our demo application, with the help of Giotto.
#. HTTP request is received by Giotto.
#. Giotto inspects the request and dispatches the request off to the ``Multiply`` program.
   Giotto knows to dispatch the request to the Multiply program
   because:

    a) The program is configured to use the 'http-get' controller, and this is a HTTP GET request.
    b) The url matches the ``name`` attribute on the program class.

#. Calls the model with the arguments from the GET vars.
#. Takes the output from the model and passes it into the view object.
#. Calls the appropriate rendering method on the view class, depending on (in this case) the ``Accept`` headers.

Now, open up your browser's javascript console (firebug if you're a firefox user).
Type in the following::

    $.ajax({url: window.location.href, success: function(a) {console.log(a)}})

You should see a json representation of the page. The HTTP controller automatically
changes the return mimetype to "application/json" when the request comes from
ajax.

Lets take a look at this program as viewed from the command line. Press `ctrl+c`
to stop the dev server.

Form the shell, run the following command::

    $ giotto-cmd multiply x=4 y=8

The output should be exactly the same. It should say `4 * 8 == 32` with the `32`
in red and the `4 * 8` in blue.

The model that is being called here is exactly the same as we saw being called from the browser.
The only difference is the way the result is visualized,
and the data moves between the user and the computer through the command lone, instead of a browser..

-----------
Using Mocks
-----------

On the GiottoProgram class, add a ``model_mock`` attribute::

    class Multiply(GiottoProgram):
        name = "multiply"
        controllers = ('http-get', 'cmd', 'irc')
        model = [multiply, {'x': 10, 'y': 10, 'product': 100}]
        view = [ColoredMultiplyView]

When you run the dev server include the ``--model-mock`` flag::

    $ giotto-http --run --model-mock

Now no matter what arguments you place in the url, the output will always be ``10 * 10 == 100``.
If your model makes calls to the database or third party service,
the ``model-mock`` option will bypass all of that.
This feature is useful for front end designers who do not need to run the full model stack in order to create HTML templates.

-----
Cache
-----

Add a ``cache`` attribute to the program::

    class Multiply(GiottoProgram):
        name = "multiply"
        controllers = ('http-get', 'cmd', 'irc')
        model = [multiply, {'x': 10, 'y': 10, 'product': 100}]
        cache = 3600
        view = [ColoredMultiplyView]

Restart the cache server (this time leave off the ``--model-mock`` flag).
Also, add a pause to the model method::

    def multiply(x, y):
        import time; time.sleep(5)
        return {'x': int(x), 'y': int(y), 'product': int(x) * int(y)}

This will simulate a heavy calculating model.
You also need to have either Redis or Memcache installed and running.
Configure the cache by adding the following to the ``cache`` variable in the concrete controller file::

    from giotto.cache import CacheWithMemcache

    cache = CacheWithMemcache(
        host='localhost'
    )

To use the redis cache, change the class to ``CacheWithRedis``.
Now when you load a page, it will take 5 seconds for the first render,
and subsequent renders will be served from cache.






















