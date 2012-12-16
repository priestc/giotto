.. _ref-cache:

=====
Cache
=====

Cache is a way to improve performance in your application.
It works by storing the return value of the model and view, so subsequent requests can skip the calculation.

Configuring cache
=================
To enable caching for your application, set a value for the ``cache`` variable in your project's ``config.py`` file.
The value must be an instance of a class derived from the ``GiottoKeyValue`` class.

RedisKeyValue
-------------
By default, this backend tries to connect to redis running on ``localhost``, port ``6379``.
To change this, pass in connection data to the constructor::

    from giotto.keyvalue import RedisKeyValue
    cache = RedisKeyValue(host="10.10.0.5", port=4000)

MemcacheKeyValue
----------------
Additionally, if you want to use memcache::

    from giotto.keyvalue import MemcacheKeyValue
    cache = MemcacheKeyValue()

By default, this backend tries to connect to memcache on ``localhost``, port ``11211``.
To change this, pass in connection data to the constructor::

    cache = MemcacheKeyValue(hosts=['10.10.0.5:11211'])

DatabaseKeyValue
----------------
You can also use a cache backend that stores its data onto the database::

    from giotto.keyvalue import DatabaseKeyValue
    cache = DatabaseKeyValue(Base, session)

You must pass in the SQLAlchemy ``Base`` class, as well as the SQLAlchemy session object.
Before this backend can be used, you must run the ``make_tables`` program to create the database tables.

LocMemKeyValue
--------------
For development, you can use the ``LocMemKeyValue`` which stores its data internally in a python dictionary::

    from giotto.keyvalue import LocMemKeyValue
    cache = LocMemKeyValue()

.. note::
    ``LocMemKeyValue`` only saves data as long as the concrete controller lives.
    For instance, while the http server is running, data will be saved,
    but if you restart the server, all data will be lost.
    This key/value backend is virtually useless with the command line controller,
    as all keys are cleared after each invocation.

DummyKeyValue
-------------
You can also use ``DummyKeyValue`` which always returns misses for all keys::

    from giotto.keyvalue import DummyKeyValue
    cache = DummyKeyValue()


Enabling caching for programs
=============================
To enable cache for a program, add a value (in seconds) to the ``cache`` attribute of the program instance::

    def square(x):
        return {'x': x * x}

    manifest = ProgramManifest({
        'squared': GiottoProgram(
            controllers=('http-get', 'cmd'),
            model=[square],
            cache=3600, # one hour
            view=MyViewClass,
        )
    })

The first request that comes into this program will be calculated.
The result of this calculation (the model's return value) will be stored in the cache.
Depending on what you've configured, this will be either Redis or Memcache.

The next request that comes in, with the same value for ``x``,
the calculation will be skipped and the value stored in cache will be returned instead.
After one hour has passed, the next request will calculate a new value.
To configure the program to never expire cache values, set the ``cache`` value to 0.
To turn off cache, either omit the cache attribute, or set it to ``None``.

Under the hood
==============
A cache key is constructed from each incoming request.
The cache key is in the following format:

    (model arguments)(program name)(mimetype)

The output of the view is what gets stored under this key.
In the example above, the cache key (if invoked from within a web browser), would be the following::

    invocation -> curl http://localhost:5000/my_program?x=12
    cache key -> {'x': 12}(my_program)(text/html)

If invoked from within the commandline controller, the cache key would be the following::

    invocation -> ./giotto-cmd my_program x=12
    cache key -> {'x': 12}(my_program)(text/cmd)