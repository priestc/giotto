In this tutorial, we will create a blog aplication that lets you:

1. Login as an author
2. Create new blogs
3. Display blogs as either an unauthenticated user, or as the author
4. Display an analytics page for each blog that shows basic statistics such as pageviews and 'likes'

First, install giotto:

    $ pip install giotto

Then run the startproject command:

    $ giotto startproject blog

This will create a new module in the current directory. Inside that directory
contains a skeleton for a giotto project:

    giotto-blog
        setup.py
        wsgi.py
        blog
            __jnit__.py
            config.py
            controllers.py
            models.py
            views.py

Now, lets build the controller for showing new blogs. In controllers.py, add the
following lines:

    @bind_controller_view('cmd', 'basic_blog')
    @bind_model(Blog.get)
    def show_blog(id)
        return locals()

Here we are defining a _controller tip_ called `show_blog`. This controller tip
has one argument, `id`. This controller tip is invoked through the command line,
and when it is, it is displayed using the `basic_blog` view.

That takes care of the controller (for now). Now we need to create the model. In
`models.py`, add the following:

    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()
    
    class Blog(Base):
        __tablename__ = 'blogs'

        id = Column(Integer, Sequence('blog_id_seq'), primary_key=True)
        title = Column(String(50))
        author = Column(String(50)) #FIXME
        body = Column(String

        