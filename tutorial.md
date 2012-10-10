First, install giotto:

    $ pip install giotto

Now create a controller file:

    $ giotto_controller --http-dev --cmd

This will create a "controller file" which will act as a gateway between your
application and the outside world. The file generated will be called 'giotto'

The `--http-dev` and `--cmd` flags tells giotto to include the plumbing for those
two "controller classes" into the controller file. Your application can now be
interacted with from the command line or through HTTP dev server. If you only
want to interact with you app through the commandline, then you could leave off
the `--http-dev`.

Inside the `giotto` file, you will see the following:

    from giotto import GiottoProgram, GiottoAbstractProgram
    from giotto.views import TEXT

    def multiply(x, y):
        return {'x': x, 'y': y, 'product': int(x) * int(y)}

    class BaseMultiply(GiottoAbstractProgram):
        name = "multiply"
        model = (multiply, )

    class MultiplyHTTP(BaseMultiply):
        controller = 'http-get'
        view = TEXT(
            '<html><body>{{obj.x}} * {{obj.y}} == {{obj.product}}</body></html>',
            mimetype="text/html"
        )

    class MultiplyCMD(BaseMultiply):
        controller = 'cmd'
        view = TEXT("{{obj.x}} * {{obj.y}} == {{obj.product}}")

The first function, `multiply` is a model method. The classes that inherit from
`GiottoProgram` are called "Giotto Programs", and they make up the basis for all
applications written with giotto. Each program contains a controller, a model
(optional) and a view. You can also add middleware and cache, but we'll deal
with those later.

These giotto programs are added by default when you add a new controller for
demonstration purposes, so you can remove them when you first start writing
real giotto apps. To see these programs in action, run the
following command:

    $ giotto http-dev

This will run the development server (you must have werkzeug installed). Now
point your browser to: http://localhost:5000/

Now lets take a look at the `multiply` program. Point your browser to:
http://localhost:5000/multiply?x=4&y=8

The browser should now be displaying `4 * 8 == 32`.

Lets take a look at this program as viewed from the commandline.

Form the shell, run the following command:

    $ giotto multiply --x=4 --y=8

The output should be exactly the same. The model function that is being called
here is exactly the same as the web version. The only difference is the way
the result is 'viewed'.