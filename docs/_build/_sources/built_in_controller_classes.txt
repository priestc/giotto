.. _ref-built_in_controller_classes:

===========================
Built-in Controller Classes
===========================

Giotto ships with three controllers classes.

HTTP
----
This controller class is used to allow program invocations via the HTTP protocol.
To run your Giotto application through HTTP,
you first must create a concrete controller file for this controller class.
Run this command from your project's root folder::

    $ giotto_project --http

This will add a file into your project folder named ``giotto-http``.
To run the development server, run the following command::

    $ ./giotto-http --run

To change the port and hostname of the development server,
edit the last line of the concrete controller file.

All requests are rendered with the ``text/html`` mimetype unless the accept headers are set otherwise.
Also, for any request that comes in through an ajax request,
the controller will attempt to render that model with the ``application/json`` mimetype.

Command Line
------------
This controller class is used to allow program invocations via the command line.
To run your Giotto application through the command line,
you first must create a concrete controller file for this controller class.
Run this command from your project's root folder::

    $ giotto_project --cmd

This will add a file into your project folder named ``giotto-cmd``.
To invoke your application, run this generated script (called a concrete controller) like so::

    $ ./giotto-cmd path/to/myprogram --var1=foo --var2=bar

This will call the ``myprogram`` program with ``var1`` and ``var2`` as arguments.

All models are rendered by the views with the ``text/cmd`` mimetype.

IRC
---
This controller class is used to allow program invocations via an IRC server
(either through a channel, or private message).
To run your Giotto application through IRC,
you first must create a concrete controller file for this controller class.
Run this command from your project's root folder::

    $ giotto_project --irc

This will add a file into your project folder named ``giotto-irc``.
Edit the generated file and add the username of the bot,
the hostname of th server you want to connect to,
and any other details you want.
To invoke your application, run this generated script (called a concrete controller) like so::

    $ ./giotto-irc

Once the bot has been connected to the server, to invoke programs, enter a channel and type the following::

    !giotto path/to/myprogram

This will call the ``myprogram`` program and return the output via the same channel.
The bot will prefix the message with the username of the user who invoked it.
the ``!giotto`` part is called the "magic token" and can be configured in the concrete controller file.

You can also invoke the bot through private message::

    /msg giotto-bot path/to/myprogram

and the bot will respond with a private message.
In this example, the bot is named "giotto-bot", but this can be configured through the concrete controller file.

All models are rendered by the views with the ``text/irc`` mimetype.

Overriding default mimetypes
----------------------------
Whenever you invoke a program, the mimetype used to render the model data is determined by that controller's default mimetype.
The default mimetypes for the HTTP, IRC and CMD controllers are ``text/html``, ``text/irc``, and ``text/cmd`` respectively.
To override this, just add the extension of your preferred type to the end of the program name::

    ./giotto-cmd path/to/program.json --x=4

This will return the result of ``program`` in JSON format instead of the default ``text/cmd``.
This also works for positional arguments::

    !giotto path/to/myprogram.txt/argument