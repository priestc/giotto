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
--------------
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