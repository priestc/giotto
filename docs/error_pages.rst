.. _ref-error_pages:

===========
Error Pages
===========
When your application throws an error, whie developing, you want to see a traceback.
When running the development server via ``./http --run``,
errors show up with a traceback and debug information.
But when your application goes into production, you do not want your users to see this debug page.
The default error page allows the user to run arbitrary python code on the server.
This is a huge security problem.
Instead, you can define an error page template.
When the HTTP controller gets an exception coming from your program,
it will return to the user your error template rendered with the details of the error.

Configuring error pages
-----------------------
In your application's config file, set the ``error_template`` variable
to the path of the template you want gitto to render in order to make your error page.
This path should be assessible by the jinja2 enviornment defined in the same config file.
This template, when rendered, will contain the following variables:

* **code** - This is the error code, such as 400, 404, 500, 403, etc.
* **exception** - The name of the exception that was caught, such as ``IndexError``, ``ValueError``, etc.
* **message** - The message that is associated with the exception (the string passed into the exception that was raised)
* **traceback** - The traceback of the exception. You may not want to render this, but its there if you want it.
  If your project's taget audience are technically capable people,
  it may benefitial to include tracebacks in the error template.

Switching between error pages and the debug page
------------------------------------------------
In your config file, there is a setting called ``debug``.
If it is set to ``True`` the debug page will be used when your application throws an exception.
Set it to ``False`` to use the error template.