.. _ref-manifests:

=========
Manifests
=========

Manifests are objects that keep track of all the programs that make up your application.
Think of them as urlconfs in django.
An example Manifests looks like this::

    from giotto.programs import Manifest
    from myapp.models import homepage, signup, auth_manifest
    
    manifest = Manifest({
        '': RootProgram(
            model=[homepage],
            view=BasicView,
        ),
        'auth': auth_manifest,
        'static': StaticServe('/var/www/static'),
        'privacy_policy': SingleStaticServe('/var/www/privacy.html'),
        'signup': [
            SignupProgram(
                view=JingaTemplateView('signup.html')
            ),
            Program(
                controllers=['http-post'],
                model=[signup]
                view=Redirection('/'),
            ),
        ]
    }

When this application is served to the outside world through a controller,
this manifest tells the controller which programs are to be available.

Manifests must contain only strings in the keys,
and only ``Program`` instances or lists of ``Program`` instances as the values.
The strings may contain any characters except for periods (``.``).

If you want to restrict a program to a certain controller,
include the controller in the ``controllers`` argument of the program::

    {
        'signup': [
            Program(
                view=JingaTemplateView('signup.html')
            ),
            Program(
                controllers=['http-post'],
                model=[signup]
                view=Redirection('/'),
            ),
        ]
    }

In the above example, all invocations except for HTTP POST requests will go to the first program.

All concrete controllers look for a project manifest object named ``manifest`` in the file named ``manifest.py``.