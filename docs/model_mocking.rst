.. _ref-mocel_mocking:

=============
Model Mocking
=============

Most development teams are composed of two "halves".
One half is composed of backend engineers who are great at writing code and working with complex software such as databases.
The other half i composed of designers, who are great with Photoshop,
but not so good with setting up databases and writing code.

Model mocking allows an application to be ran in an environment where the database does not need to be ran.
The model part of a program is completely ignored, and the mock object is returned instead::

    from giotto.programs import Program
    from giotto.views import BasicView
    import psycopg2

    def square(x):
        """
        Connect to a postgres server and multiply two numbers together.
        """
        conn = psycopg2.connect("dbname=test user=postgres")
        cur = conn.cursor()
        cur.execute("SELECT %s * %s;", (x, x))
        result = cur.fetchone()
        return {'x': x, 'square': result[0]}

    class Square(Program):
        controllers = ('http-get', 'cmd')
        model = [square, {'x': 12, 'square': 144}]
        view = BasicView

When this application is ran normally, a connection must be made to a posgres server.
If the server is not running, the program would crash.
Not only that, but in some cases, there must be data in the database for this program to execute properly.
This can cause issues that make developing applications difficult.

If you run the http server with the ``--model-mock`` option,
the model function will get bypassed.
No connection is attempted to a PostgreSQL server.
The value of the mock will be used instead.

Defining a model mock
---------------------

The model mock is defined in the program as the second item in the ``model`` list::

    model = [model_func, model_mock]

When you define a model mock, make sure the mock is in the same format what the model returns.