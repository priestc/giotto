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
Run this command from your project's root folder:

    $ giotto_project --http

This will add a file into your project folder named ``giotto-http``.
To run the development server, run the following command:

    $ ./giotto-http --run

To change the port and hostname of the development server,
edit the last line of the concrete controller file.

Command Line
------------

This controller class is used to allow program invocations via the command line.
To run your Giotto application through the command line controller class,
you first must create a concrete controller file for this controller class.
Run this command from your project's root folder:

    $ giotto_project --cmd

This will add a file into your project folder named ``giotto-cmd``.
To invoke your application, run this generated script (called a concrete controller) like so:

    $ ./giotto-cmd path/to/myprogram --var1=foo --var2=bar

This will call the ``myprogram`` program with ``var1`` and ``var2`` as arguments.

IRC
---