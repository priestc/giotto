.. _ref-creating_your_own_controllers:

=============================
Creating your own controllers
=============================

Custom controllers are implemented as a subclass of ``giotto.controllers.GiottoController``.
A custom controller can be used to run a giotto application through a new mode of invocation.

For instance, you could write a controller that monitors an email inbox.
The controller would take in any new message, parse the message,
and reply to with a new message.

All custom controller classes must implement the following methods:

.. function:: get_raw_data()

This function returns the "payload data" of the incoming request.
The HTTP controller returns the GET or POST parameters.
A dictionary should be returned.

.. function:: get_invocation()

The function should return the name of the invocation, e.g. "path/to/program.txt"
The HTTP controller returns the value of ``request.path``

.. function:: mimetype_override()

All responses from a controller are rendered with the mimetype that is set in
the property ``default_mimetype`` unless this function returns a different one.
For instance, all invocations from HTTP are rendered as text/html,
with the exception of when a request is made with alternate ``Accept`` headers.
If this function returns ``None``, then the value in ``default_mimetype`` is used.

.. function:: get_controller_name()

This should return the name of the controller.

.. function:: get_concrete_response()

This function is used to return the response object that is specific to the controller context.
For instance, the HTTP controller returns a werkzeug ``Response`` object.
This function should call ``get_data_response()``, which returns the output of the view.
Keep in mind, ``get_data_response()`` can throw an error,
so ``get_concrete_response()`` must try to catch these errors and expose them properly through the controller.

.. function:: get_primitive(primitive)

Primitives are the abstracted interface between the controller and the model.
This function should extract the proper data from the ``raw_data`` dictionary (see above).
Not all primitives need to be implemented, but it is a good idea to implement as many as possible.

Concrete controller template
----------------------------

Additionally, the controller file must also include a template for creating the concrete controller.
The snippet should be named ``[name]_execution_snippet``, where ``[name]`` is the controller name.
The snippet will be added to the bottom of the concrete controller file and is used to instantiate the controller class.