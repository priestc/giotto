.. _ref-deployment:

================
Deploying Giotto
================

uWSGI
-----
When creating the concrete controller file, make sure you include the ``--http`` option.
Install uwsgi::

    pip install uwsgi

and run the server by using the concrete controller file as the wsgi file::

    uwsgi --http :5000 --wsgi-file http

gunicorn
--------
Install gunicorn::

    pip install gunicorn

Gunicorn works slightly differently than uwsgi.
Some modifications of the automatically generated concrete controller is required.

Rename the ``http`` file to ``http.py``.

The run the following command::

    gunicorn --workers=1 --log-level=debug http:application

Apache and Nginx
----------------
Since these servers are not pure python, it is more tricky to get them set up.
Basically the steps are the same for deploying any other wsgi application.
Use ``http`` file as the WSGI file.