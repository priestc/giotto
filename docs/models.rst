.. _ref-models:

======
Models
======

A model is a function that takes in values from the controller, and returns values to the view.
Giotto is very hands off when it comes to the model.
Your model function can call other model functions, it can call facebook's API,
it can talk to a database, it can do anything.
Giotto comes with some helpers to make using SQLAlchemy easier, but it's use is completely optional.
Giotto, unlike some popular popular web frameworks, can be ran without any database whatsoever.

Integration with SQLAlchemy
---------------------------
When defining a model, you should use the baseclass that comes out of the ``better_base`` function found in ``giotto.utils``.
Models descending from this base class will have a ``todict`` method which Giotto uses to easily convert your model to JSON.

In your project's config file, define the base class::

    from giotto.utils import better_base
    Base = better_base()

Now, when defining your model class, use this baseclass::

    from giotto.config import Base
    class MyModel(Base):
        """
        This is a model
        """

(anything in your config file will be available by importing from ``giotto.config``).

You must also define a ``engine`` and ``session`` variable in the config file.
``engine`` is the result of ``create_engine`` from sqlalchemy.
``session`` is the result of ``sessionmaker``.
The default config file created by the ``giotto`` command line utility contains boilerplate for defining these variables.


Creating tables
---------------
Add the manageent manifest to your project::

    from giotto.programs import management_manifest, ProgramManifest

    manifest = ProgramManifest({
        'mgt': management_manifest
    })

And to create the tables, do the following command::

    $ ./cmd mgt/make_tables

This program, by default, will only be available via the command line controller.
The ``make_tables`` command will only find models you have defined with that baseclass,
if that model has been imported into your project's manifest.
This is unlike Django and other frameworks, that use a ``models.py`` convention.

InvalidInput
------------
When a model recieves data from a POST request, and the data does not validate,
the model should raise the ``giotto.exceptions.InvalidInput`` exception.
The controller will catch this exception and re-render the get portion of the request.
When the exception is raised, you can add key word arguments to the exception constructor describing the dat that was invalid.
As an example, consider the following model function that only accepts numbers below 100::

    from giotto.exceptions import InvalidInput

    def multiply(x, y):
        try:
            x = int(x or 0)
            y = int(y or 0)
        except:
            raise InvalidInput("Numbers only", x={'value': x}, y={'value': y})

        if x > 100 and y > 100:
            raise InvalidInput('x and y are too large', x={'message': 'too large', 'value': x}, y={'message': 'too large', 'value': y})
        if x > 100:
            raise InvalidInput('x is too large', x={'message': 'too large', 'value': x}, y={'value': y})
        if y > 100:
            raise InvalidInput('y is too large', y={'message': 'too large', 'value': y}, x={'value': x})

        return {'x': x, 'y': y, 'product': x * y}

The values of the keyword argument should be a dictionary with two keys, ``value`` and ``message``.
