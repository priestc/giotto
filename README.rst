What is Giotto?
===============

Giotto is a python web framework. It encourages a functional style where model, view and controller code is strongly decoupled.

Key Features of Giotto include:

* Extremely terse code. A full featured blog application is under 300 lines of code (including templates)
* Generic views, generic models and multiple pluggable controllers.
* Free RESTful interface along with your normal "browser POST" CRUD site.
* Functional CRUD patterns that do away with the need for django-style form objects.
* Automatic URL routing.
* Built in cache (supports Redis and Memcache, and an API for supporting any other engines)
* SQLAlchemy for database persistence.
* Jinja2 for HTML templates (with an API for extending for other template engines)

Getting started
===============

Install and create base project files::

    pip install giotto
    mkdir demo
    giotto create http

Now your project is initialized. Open the ``manifest.py`` and add the following::

    from giotto.programs import ProgramManifest, GiottoProgram
    from giotto.views import jinja_template, BasicView

    def multiply(x, y):
        x = int(x or 0)
        y = int(y or y)
        return {'x': x, 'y': y, 'result': x * y}

    manifest = ProgramManifest({
        'multiply': GiottoProgram(
            model=[multiply],
            view=BasicView(
                html=jinja_template('multiply.html'),
            ),
        ),
    })

Now create a file called ``multiply.html``::

    <!DOCTYPE html>
    <html>
        <body>
            {{ data.x }} * {{ data.y }} == <strong>{{ data.result }}</strong>
        </body>
    </html>

Or if you're too lazy to make a template,
set the ``view`` keyword argument to just ``BasicView()`` to use the generic view.

Run the development server::

    $ giotto http --run

Point your browser to ``http://localhost:5000/multiply?x=3&y=3``.
Additionaly, try ``http://localhost:5000/multiply.json?x=3&y=3``.
You can also invoke your multiply program through the command line::

    $ giotto create cmd
    $ giotto cmd multiply --x=4 --y=2

Also::

    $ giotto cmd multiply.html --x=4 --y=2

You can also use positional arguments::

    $ giotto cmd multiply/4/6

Links:

* To discuss Giotto, please visit the Google Group_
* Read Giotto's documentation_.
* Check out giottoblog_, a full featured blog application written with the Giotto framework.

.. _Group: https://groups.google.com/forum/#!forum/giotto-framework/
.. _giottoblog: https://github.com/priestc/giottoblog/
.. _documentation: http://giotto.readthedocs.org/en/latest/index.html