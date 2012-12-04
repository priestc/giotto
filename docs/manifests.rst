.. _ref-manifests:

=========
Manifests
=========

Manifests are objects that keep track of all the programs that make up your application.
Think of them as urlconfs in django.
An example Manifests looks like this::

    manifest = ProgramManifest({
        '': RootProgram(),
        'auth': {
            'login': LoginProgram(),
            'logout': LogoutProgram(),
        },
        'static': StaticServe('/var/www/static'),
        'privacy_policy': SingleStaticServe('/var/www/privacy.html'),
        'signup': SignupProgram(),
    }

When this application is served to the outside world through a controller,
this manifest tells the controller which programs are to be available.

You can also nest manifests::

    login_manifest = ProgramManifest({
        'login': LoginProgram(),
        'logout': LogoutProgram(),
    }

    manifest = ProgramManifest(
        '': RootProgram(),
        'auth': login_manifest,
        'static': StaticServe('/var/www/static/'),
        'privacy_policy': SingleStaticServe('/var/www/privacy.html'),
        'signup': SignupProgram(),
    }

Manifests must contain only strings in the keys, and only ``GiottoProgram``s as the values.
The strings may contain any characters except for periods (``.``).

All concrete controllers look for a project manifest object named ``manifest`` in the file named ``manifest.py``.