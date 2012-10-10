First, install giotto:

    $ pip install giotto

Now create a controller file:

    $ giotto_controller --http --cmd

This will create a "controller file" which will act as a gateway between your
application and the outside world. The fine generated wll be called 'giotto'
and it is what you will use to interact with your application.

The `--http` and `--cmd` flags tells giotto to 'instantiate' those two controller
classes into your controller file. Your application can now be interacted with
from the command line or through HTTP. If you only want to interact with you app
through the commandline, then you could leave off the `--http`.

Inside the `giotto` file, you will see the following:

    from giotto import GiottoProgram, GiottoAbstractProgram
    from giotto.views import TEXT

    class HelloWorld(GiottoProgram):
        name = ""
        controller = 'http-get'
        view = TEXT("Hello {{obj.name }}")

    def multiply(x, y):
        return {'x': x, 'y': y, "product": x * y}

    class BaseMultiply(GiottoAbstractProgram):
        name = "multiply"
        model = (multiply, )

    class MultiplyHTTP(BaseMultiply):
        controller = 'http-get'
        view = TEXT("<span style='color: blue'>{{obj.x}} * \
            {{obj.y}}</span> == <span style='color: red'>{{obj.product}}</span>")

    class MultiplyCMD(BaseMultiply):
        controller = 'cmd'
        view = TEXT("{{obj.x}} * {{obj.y}} == {{obj.product}}")

These classes are called "Giotto Programs". They represent pieces of a larger
application. Each program contains a controller, a model (optional) and a view.
You can also add middleware and cache, but we'll deal with those later.

These giotto programs are added by default when you add a new controller, so
you can remove them if you want. To see these programs in action, run the
following command:

    $ giotto http

This will run the development server (you must have werkzeug installed). Now
point your browser to: http://localhost:5000/

You should see "Hello World" printed in the browser window. Now try with custom
name by pointing your browser to http://localhost:5000/?name=Tommy

The browser should now display "Hello Tommy".

Now lets take a look at the `multiply` program. Point your browser to:
http://localhost:5000/multiply?x=4&y=8

The browser should now be displaying `4 * 8 = 32` with the 32 in red and the
4 * 8 in blue.

Lets take a look at this program as viewed from the commandline.

Form the shell, run the following command:

    $ giotto multiply --x=4 --y=8

The output should be exactly the same. The model function that is being called
here is exactly the same as the web version. The only difference is the way
the result is 'viewed'.