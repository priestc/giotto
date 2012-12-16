.. _ref-view_classes:

============
View Classes
============

View classes take in data that the model returns, and returns data that is viewable.
For instance, if the model returns a simple dictionary:

    {'x': 3, 'y': 10, 'result': 30}

The the view's job is to take this data and return a visual representation, such as::

    3 * 10 == 30

or::

    <!DOCTYPE html>
    <html>
        <body>
            <p>3 * 10 == 30</p>
        </body>
    </html>

Creating View Classes
---------------------

All view classes must descent from ``giotto.views.BaseView``.
Each class needs to implement at least one mimetype method::

    from giotto.views import BaseView

    class MyView(BaseView):
        def text_plain(self, result):
            return "%(x)s * %(y)s == %(result)s" % result

Each method is named after the mimetype it returns (with the ``/`` replaced with an underscore),
and take one argument that will be the value that the model returns.
When creating views, make sure there is no 'impedance mismatch' between the data that the model returns,
and the data the view is written to take in.
For instance, the above mimetype method is designed to display a dictionary with three keys (``x``, ``y``, and ``result``).
If the model was changed to return a list, this view method will crash.

Return values
-------------

Each mimetype render method should return either a string::

    return "return a string"

or a dictionary with body and mimetype tags::

    return {'body': "this is whats returned, 'mimetype': 'text/plain'}

Not all ``text_html`` render methods will return ``text/html`` content.

BasicView
---------

There is a view class called ``BasicView`` that was created to be a quick and dirty way to view most any data.
While developing your application, it is a good idea to use ``BaseView`` until you have settled on a consistent data type that your model returns.