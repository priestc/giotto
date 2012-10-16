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
Install gunicorn::

    pip install gunicorn

Gunicorn works slightly differently than uwsgi.
Some modifications of the automatically generated concrete controller is required.

Rename the ``giotto-http`` to ``http_gunicorn.py``. (remove the '-' and add '.py' to the end)

The run the following command::

    gunicorn --workers=1 --log-level=debug giotto_gunicorn:application

Apache and Nginx
----------------
Since these servers are not pure python, it is more tricky to get them set up.
Basically the steps are the same for deploying any other wsgi application.
Use ``giotto-http`` file as the WSGI file.