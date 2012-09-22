What is Giotto?
===============

Giotto is a python application framework. Not quite a web framework, but it does
include plumbing for deploying applications through a web server.

Giotto's motto is "An application framework for idealists with no deadlines"

This document is a work in progress. Since Giotto is still being conceptualized
and written, this document will

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

Features
========

* Completely working commandline interface as well as web interface out of the box
* Giotto automatically configures the urls for you. No more dealing with messy regex
based urls to define!

Primitives
==========

When writing model methods, in the function declaration, you can define primitives
which expand to data requested automatically from any controller.

    from giotto import primitives

    def view(data)
        return "logged in as %s" % data['user']

    @bind_controller('http-1.1-get', view)
    @bind_controller('cmd', view)
    def currently_logged_in(user=primitives.LOGGED_IN_USER):
        return {'user': user}

Now when you invoke this function from either the commandline or via http, the
value of `user` will be the currently logged in user. In a http context, the user
will come from a cookie. From the commandline, the currently logged in user will
be extracted from an enviornment variable. How exactly this data is extracted is
a function of the controller module (defined as 'http' and 'cmd' above), and is
configurable.

Example Application:
====================

    from giotto.primitives import RAW_PAYLOAD, LOGGED_IN_USER
    from giotto.exceptions import NotFound, ImproperInput

    def blog_html(blog, errors=None):
        """
        For showing a blog in an HTML context
        """
        return """<html><body>
                    <h1>{blog[title]}</h1>
                    <h2>by {blog[author]}</h2>
                    <p>{blog[body]}</p>
                  </body></html>""".format(blog=blog)

    def blog_new(blog, errors=None):
        """
        After a blog is created from the command line, return a message
        telling the usser the new blog url 
        """
        url = get_invocation('http-1.1-get', blog.__class__.view, {'id': blog.id})
        return "New blog created! see at %s" % url

    def commandline_blog(blog, errors=None):
        """
        For showing a blog on the commandline.
        """
        if errors:
            return str(errors)
        return "{blog[title]}\nby {blog[author]}\n\n{blog[body]}".format(blog=blog)


    @bind_controller('cmd', blog_new)
    @bind_controller('http-1.1-post', blog_html)
    def crete_new_blog(title, body, author=LOGGED_IN_USER)
        if len(title) > 50:
            raise ImproperInput("title too long")

        # Call the model to save the blog in whatever data store is used
        return Blog.create(title, body, author)

    @bind_controller('cmd', commandline_blog)
    @bind_controller('http-1.1-get', blog_html)
    def view_blog(id)
        # call to model
        blog = Blog.filter(disabled=False).get(id=id)
        if not blog:
            raise NotFound("invalid blog id: %s" % id)
        return blog

Usage:
======

    $ curl -d "title='my blog'&author=william&body='my blog body'" http://myblog.com/Blog/create_new_blog
    <html><body>
        <h1>my blog</h1>
        <h2>by william</h2>
        <p>my blog body</p>
    </body></html>

    $ giotto Blog.create_new_blog --title='Second blog' --author=todd --body="another blog"
    New blog created! see at http://myblog.com/Blog/view?id=2

    $ giotto Blog.view --id=2
    Second blog
    by todd

    another blog

    $ giotto Blog.create_new_blog --title='way more than 50 chars!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    Error: ('title too long')

    