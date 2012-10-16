.. _ref-middleware:

==========
Middleware
==========

All middleware classes must implement a method for each controller name.
For input middleware, each method should take one argument, `request`,
and return a new `request` object::


    class SomeInputMiddleware(object):
        def http(self, request):
            do_some_stuf()
            return request

        def cmd(self, request):
            do_some_stuf()
            return request

        def sms(self, request):
            do_some_stuf()
            return request

Output middleware should take two arguments, `request` and `response`,
and should return a new `response` object::

    class SomeOutputMiddleware(object):
        def http(self, request, response):
            do_some_stuf()
            return response

        def cmd(self, request, response):
            do_some_stuf()
            return response

        def sms(self, request, response):
            do_some_stuf()
            return response

The appropriate method will be called depending on how the program has been
invoked.