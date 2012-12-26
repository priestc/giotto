.. _ref-error_pages:

===========
Error Pages
===========
When your application throws an error, whie developing, you want to see a traceback.
When running the development server via ``./http --run``,
errors show up with a traceback and debug information.
But when your application goes into production, you do not want your users to see this debug page.
Instead, you can define an error page template.
When the HTTP controller gets an exception coming from your program,
it will return to the user your error template rendered with the details of the error.

Configuring error pages
--------------------------
In your application's config file, set the ``error_template`` variable
to the path of the template you want gitto to render in order to make your error page.
This path should be assessible by the jinja2 enviornment defined in the same config file.
This template, when rendered, will contain the following variables:

* **code** - This si the error code, such as 400, 404, 500, 403, etc.
* **exception** - The name of the exception that was caught, such as ``IndexError``, ``ValueError``, etc.
* **message** - The message that is associated with the exception (the string passed into the exception that was raised)
* **traceback** - The traceback of the exception. You may not want to add this, but its there if you want it there.
  If your project's taget audience are technically capable people,
  it may benefitial to include tracebacks in this template.