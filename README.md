![logo](http://i.imgur.com/Ckokr.png)

What is Giotto?
===============

Giotto is a python application framework. Not quite a web framework, but it does
include plumbing for deploying applications through a web server.

Giotto's motto is "An application framework for idealists with no deadlines"

This document is a work in progress. Since Giotto is still being conceptualized
and written, this document will change often.

To discuss Giotto, please visit the [google group](https://groups.google.com/forum/#!forum/giotto-framework)
To read Giotto's documentation, go [here](http://giotto.readthedocs.org/en/latest/index.html)

Why?
====

The point of giotto is to avoid writing any controllers. All you write is the
model, and the views. Giotto takes care of the rest.

Write our models once, and reuse them across any controller you want!

Philosophy
==========

* Convention Over Configuration - It may seem like a bummer at first to not be
able to fine-tune configure every aspect of giotto. But in the long run, this
approach is best, as each giotto user does things the same way. Giotto does not
let you shoot yourself in the foot.

* Forward thinking backwards compatability - Giotto will release major versions
that break backwards compatability more often than most projects. For instance,
Giotto 2.x will not be backwards compatable to Giotto 1.x, etc. Point releases will
occur

* Document driven - It is very important that all aspects of giotto are documented
before they are written.

* Giotto should make you do the right thing - It should be very hard to create
complex spaghetti code when using giotto.

* Everything that other frameworks can do, giotto should be able to do - Numerous
times in the development process, giotto's API had radically changed when it has
become known that other frameworks can do things much easier than giotto.

Features
========

* Completely working commandline interface as well as web interface out of the box

* Giotto automatically configures the urls for you. No more dealing with messy regex
based urls to define!

Primitives
==========

Each controller implements a set of 'primitives' that your controller tips can
use without coupling your application to any one controller. Eample:

    class ShowBlog(GiottoAbstractProgram):
        name = 'show_blog'
        model = (Blog.get, )

    class ShowBlogHTTP(ShowBlog)
        controller = 'http-get'
        view = HTML('blog.html')

    class Blog(object):
        @classmethod
        def get(cls, id, retrieving_user=LOGGED_IN_USER):
            ...

In the above snippet, `LOGGED_IN_USER` on the model method is a special
'primitive' object that represents the currently logged in user. In an HTTP
context, this data comes from a cookie that is set my some authentication
middleware. We can subclass this application, and change the controller:

    class ShowBlogCMD(ShowBlog):
        controller = 'cmd'
        view = JSON

In this case, `LOGGED_IN_USER` comes from the CMD controller, and is implented
by looking at the enviornment of the commandline where this program is invoked.
The details of how this information gets to the model is an implementation
detail of the controller class, and is of no concern for the model developer.


Middleware
==========

All middleware classes must implement a method for each controller name. For
input middleware, each method should take one argument, `request`, and return a
new `request` object. Output middleware should take two arguments, `request` and
`response`, and should return a new `response` object.

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

    class SomeOutputMiddleware(object):
        def http(self, request, reqponse):
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