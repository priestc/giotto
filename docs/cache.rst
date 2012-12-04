.. _ref-cache:

=====
Cache
=====

Cache is a way to improve performance in your application.
It works by storing the return value of the model and view, so subsequent requests can skip the calculation.

Configuring cache
-----------------
In your project's ``config.py``, add the following::

    from giotto.cache import CacheWithRedis
    cache = CacheWithRedis() 

or if you want to use memcache::

    from giotto.cache import CacheWithMemcache
    cache = CacheWithMemcache()

You can also add parameters to the ``CacheWith*`` class such as port and host.


Enabling caching for programs
-----------------------------

To enable cache for a program, add a value (in seconds) to the ``cache`` attribute of your program class::

    def my_model(x):
        return {'x': x * x}

    class MyProgram(GiottoProgram):
        name = 'my_program'
        controllers = ('http-get', 'cmd')
        model = [my_model]
        cache = 3600 # one hour
        view = MyViewClass

The first request that comes into this program will be calculated.
The result of this calculation (the model's return value) will be stored in the cache.
Depending on what you've configured, this will be either Redis or Memcache.

The next request that comes in, with the same value for ``x``,
the calculation will be skipped and the value stored in cache will be returned instead.
After one hour has passed, the next request will calculate a new value.
To configure the program to never expire cache values, set the ``cache`` value to 0.
To turn off cache, either omit the cache attribute, or set it to ``None``.

Under the hood
--------------

A cache key is constructed from each incoming request.
The cache key is in the following format:

    (model arguments)(model name)(mimetype)

The output of the view is what gets stored under this key.
In the example above, the cache key (if invoked from within a web browser), would be the following::

    invocation -> curl http://localhost:5000/my_program?x=12
    cache key -> {'x': 12}(my_model)(text/html)

If invoked from within the commandline controller, the cache key would be the following::

    invocation -> ./giotto-cmd my_program x=12
    cache key -> {'x': 12}(my_model)(text/cmd)