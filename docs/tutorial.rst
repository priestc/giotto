.. _ref-tutorial:

===========================
Getting Started with Giotto
===========================

First, install giotto::

    $ pip install giotto==0.11.0

.. note::
    Giotto is very actively under development, The version on pypi is most definitely stale.
    Instead of the above command, you can optionally install the latest version from github::
        
        $ pip install git+git://github.com/priestc/giotto.git

Now create a new directory::

    $ mkdir demo

and inside that directory, run this command::

    $ cd demo
    $ giotto create http cmd --demo

This will create a ``manifest.py`` file, which contains your program manifest.
It will also create a series of "concrete controller files",
which will act as a gateway between your application and the outside world.
The concrete controller files will be called ``http_controller.py`` and ``cmd_controller.py``
This utility will also add a ``config.py``, ``secrets.py`` and ``machine.py`` file,
which will be where you add database connection information (and other things).

If you only want to interact with you application through the command line,
then you could leave off the ``http`` flag when calling ``giotto`` (and vice versa).
The option ``--demo`` tells giotto to include a simple "multiply" program to demonstrate how giotto works.

Inside the ``manifest.py`` file, you will see the following::

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

    manifest = Manifest({
        'multiply': Program(
            controllers = ('http-get', 'cmd', 'irc'),
            model=[multiply, {'x': 3, 'y': 3, 'product': 9}],
            view=ColoredMultiplyView
        )
    })

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

    $ giotto http --run

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

    $.ajax(window.location.href).done(function(r) {console.log(r)})

You should see a json representation of the page. The HTTP controller automatically
changes the return mimetype to "application/json" when the request comes from
ajax.

Lets take a look at this program as viewed from the command line. Press `ctrl+c`
to stop the dev server.

Form the shell, run the following command::

    $ giotto cmd multiply x=4 y=8

The output should be exactly the same. It should say `4 * 8 == 32` with the `32`
in red and the `4 * 8` in blue.

The model that is being called here is exactly the same as we saw being called from the browser.
The only difference is the way the result is visualized,
and the data moves between the user and the computer through the command lone, instead of a browser..

-----------
Using Mocks
-----------

On the Program object, add a ``model_mock`` object to the list along with the model.
A model mock is an object that gets returned in lieu of executing the model function.
This object should be the same form as what the model returns::

    manifest = Manifest({
        'multiply': Program(
            controllers=('http-get', 'cmd', 'irc'),
            model=[multiply, {'x': 10, 'y': 10, 'product': 100}],
            view=ColoredMultiplyView,
        )
    })

When you run the dev server include the ``--model-mock`` flag::

    $ giotto http --run --model-mock

Now no matter what arguments you place in the url, the output will always be ``10 * 10 == 100``.
If your model makes calls to the database or third party service,
the moel mock option will bypass all of that.
This feature is useful for front end designers who do not need to run the full model stack in order to create HTML templates.
This feature is also sometimes called "generic models".

-----
Cache
-----

Add a ``cache`` attribute to the program::

    manifest = Manifest({
        'multiply': Program(
            controllers = ('http-get', 'cmd', 'irc'),
            model=[multiply, {'x': 10, 'y': 10, 'product': 100}],
            cache=3600,
            view=ColoredMultiplyView
        )
    })

Restart the cache server (this time leave off the ``--model-mock`` flag).
Also, add a pause to the model method::

    def multiply(x, y):
        import time; time.sleep(5)
        return {'x': int(x), 'y': int(y), 'product': int(x) * int(y)}

This will simulate a heavy calculating model.
You also need to have either Redis or Memcache installed and running.
Configure the cache by setting the following to the ``cache``
variable in the ``machine.py`` file::

    cache_engine = 'memcache'
    cache_host = 'localhost'

To use the redis cache, change the engine to ``redis``.
Now when you load a page, it will take 5 seconds for the first render,
and subsequent renders will be served from cache.


----------------
Now You're Done!
----------------

Thats it in a nutshell. To learn more, read around the docs, and build things!