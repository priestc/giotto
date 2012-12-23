.. _ref-introduction:

============
Introduction
============

Giotto is a framework for building applications ina functional style.
It is based on the concept of Model, View and Controllers.

The framework is designed to enforce a clean style that results in code that is maintainable over a long period.


Invocation cycle
----------------

.. image:: http://i.imgur.com/1YszO.png

The invocation cycle is as folows:

1. The controller process is started.
   An example of a controller process is Apache, or gunicorn.
   A manifest is given to the controller process when it is started.
   All incoming requests to the controller process will be routed to a program contained within the manifest.
   A manifest is just a collection of programs.

2. A user makes a request to the controller process.
   This can be a web request, or a command line invocation, or any other action that is handled by a controller process.

3. The controller packages up the request into a ``request`` object.
   In the image above, the invocation being depicted is basically a user saying, 
   "Give me the contents of blog # 3 in an html document"

4. That request in inspected by the controller.
   The appropriate program is determined from the manifest based on attributes of the request.
   In the image above, the path of the request (``/blog``) determines the program.
   A program is a collection of a model, a view, a cache expire time, a set of input middleware classes, and a set of output middleware classes.

5. Once the program has been determined, the request object is routed through the input middleware.
   The middleware objects are functions that take in a request object, and return a request object.

6. After each input middleware class associated with the program has been ran,
   the controller sends off data to the model, and the model is executed.
   In the example above, the model is a function that retrieves blog data from a database.
   The data it requires is the ID of the blog. In this case, the ID is 3.

7. When the model is done, it returns its data, and it gets passed in directly to the view.
   At the same time, the controller sends the mimetype of the invocation to the view as well.
   In the example, the mimetype is ``text/html``.

8. The view renders the blog data into an HTML document.
   The data is then passed onto the controller, but before that, it is stored in the cache.
   How long the data will stay in the cache is an attribute of the program.

9. The controller takes this html document and packages it up into a response object.

10. This response object is passed on through the output middleware classes.
    Such classes are very similar to input middleware classes, except they take in a response, and return a response.

11. That response gets returned to the user.