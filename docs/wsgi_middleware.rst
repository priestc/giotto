.. _ref-wsgi_middleware:

===============
WSGI Middleware
===============

Giotto interacts with the WSGI specification very well.
To add WSGI middleware to your application, edit the ``http`` file::

    application = make_app(manifest, model_mock=mock)

    if not config.debug:
        from raven import Client
        from raven.middleware import Sentry

        application = Sentry(
            application,
            Client(config.sentry_dsn)
        )

        application = error_handler(application)

``raven`` is a tool that is used to report errors in our application to a sentry server.