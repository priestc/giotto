What is Giotto?
===============

Giotto is a python application framework. Not quite a web framework, but it does
include plumbing for deploying applications through a web server.

Giotto's motto is "An application framework for idealists with no deadlines"

This document is a work in progress. Since Giotto is still being conceptualized
and written, this document will change often.

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

    def view(data):
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
    from giotto import bind_controller, bind_model, get_invocation

    ###############
    ## Views
    ###############

    def blog_new(blog, errors=None):
        """
        After a blog is created from the command line, return a message
        telling the usser the new blog url.
        """
        url = get_invocation('http-1.1-get', 'view_blog', args={'id': blog.id})
        return "New blog created! see at %s" % url

    def commandline_blog(blog, errors=None):
        """
        For showing a blog on the commandline.
        """
        if errors:
            return errors
        return "{blog.title}\nby {blog.author.name}\n\n{blog.body}".format(blog=blog)

    ###############
    ## Models
    ###############

    class Blog(object):
        """
        The model for the Blog application. This class handles saving to the database
        and validating data coming in and out of the database. An instance of this
        class represents a blog.
        """

        body = ''
        author = None
        title = ''

        def validate(self):
            """
            Validate a blog instance. Return the things wrong with it.
            """
            errors = []
            if len(title) > 50:
                errors.append("title too long")
            if body == '':
                errors.append("body can't be empty")

            return errors or None

        @classmethod
        def get(cls, **kwargs):
            """
            Get blog data from the database and return it.
            """
            if 'id' in kwarg.keys():
                return redis.get(id=kwargs['id'])
            raise NotImplementedError('only get by id supported at this time')

        @classmethod
        def create(cls, title, body, author_id):
            """
            Create a new blog and make sure the data is valid. Returns the database
            ID of the newly created blog.
            """
            author = Author.get(id=author_id) # another model
            blog = cls(title=title, body=body, author=author)
            
            errors = blog.validate()
            if errors:
                raise InvalidInput("\n".join(errors))
            
            new_blog = redis.save(blog)
            return new_blog

        @classmethod
        def edit_blog(cls, id, title, author, body):
            blog = cls.get(id=id)
            blog.title = title
            blog.author = author
            blog.body = body

            errors = blog.validate()
            if errors:
                redis.save(blog)
            else:
                raise InvalidInput("/n".join(errors))
            return blog

    ########
    ## Apps
    ########

    from giotto.exceptions import InputError
    from giotto.control import Redirection

    from models import Blog
    from views import HTML, commandline_blog

    class ShowBlog(GiottoApp):
        name = "show_blog"
        model = Blog.get
        controller_tip = ('id', )

    class ShowBlogHttp(ShowBlog):
        controller = 'http-get'
        view = HTML('blog.html')
        output_middleware = [HTMLMinify]

    class ShowBlogCMD(ShowBlog):
        controller = 'cmd'
        view = commandline_blog

    # ---

    class NewBlog(GoittoApp):
        name = "create_new_blog"

    class NewBlogHTMLForm(NewBog):
        controller = 'http-get'
        controller_tip = ('title', 'body')
        model = lambda x: x
        view = HTML('new_blog.html')

    class NewBlogSubmit(NewBlog):
        conroller = 'http-post'
        controller_tip = ('title', 'body', LOGGED_IN_USER)
        model = Blog.create
        view = Redirection('show_blog')

        def on_error(exc, controller_tip):
            if exc is InputError:
                return Redirection(NewBlogHTMLForm, args=controller_tip)


Usage:
======

Creating blogs
--------------

From command line:

    $ giotto create_new_blog --title='Second blog' --author=todd --body="another blog"
    New blog created! see at http://myblog.com/view_blog?id=2

From http:

    $ curl -d "title=title&author=william&body=body" http://myblog.com/create_new_blog
    <html><body>
        <h1>title</h1>
        <h2>by william</h2>
        <p>body</p>
    </body></html>   

Viewing blogs
-------------

From command line:

    $ giotto view_blog --id=2
    Second blog
    by todd

    another blog

From http:

    $ curl http://myblog.com/view_blog?id=2
    <html><body>
        <h1>title</h1>
        <h2>by william</h2>
        <p>body</p>
    </body></html>    

Error Reporting
---------------

From command line:

    $ giotto create_new_blog --title='way more than 50 chars!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    Error: ('title too long', 'body can't be empty')

From http:

    $ curl -i -d "title=reallylongtitlethatisover50chars!!!!!!!!!!!!!!!!!!!!!" http://myblog.com/create_new_blog
    HTTP/1.1 400 Bad Request
    Server: nginx/1.0.12
    Date: Mon, 20 Feb 2012 11:15:49 GMT
    Content-Type: text/html;charset=utf-8

    <html>title too long
    body can't be empty</html>