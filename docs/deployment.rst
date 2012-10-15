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

    uwsgi --http :5000 --wsgi-file giotto-http

gunicorn
--------

Install gunicorn:

    pip imnstall gunicorn

Gunicorn works slightly different that uwsgi.
Some modifications of the automatically generated concrete controller is required.

Rename the ``giotto-http`` to ``http_gunicorn.py``.

The run the following command:

    gunicorn --workers=1 --log-level=debug giotto_gunicorn:application