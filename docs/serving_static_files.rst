.. _ref-serving_static_files:

====================
Serving Static Files
====================

Handling Static files is very simple in Giotto.
Just add the ``ServeStatic`` program to your manifest::

    from giotto.contrib.static.programs import StaticServe

    manifest = Manifest({
        'static': StaticServe('/var/www/static_files')
    })

When you run this manifest through a controller, you can access the static files like so::

    ./giotto-cmd static/text/myfile.txt

The file at ``/var/www/static_files/text/myfile.txt`` will be displayed as if you had ``cat`` the file.

SingleStaticServe
-----------------
This program is useful to place a single file onto the manifest::

    manifest = Manifest({
        'static': StaticServe('/var/www/static_files'),
        'favicon': StaticServe('/var/www/static_files/favicon.ico'),
    })

The name you give the ``SingleStaticServe`` program in your manifest has to have the extension omitted.