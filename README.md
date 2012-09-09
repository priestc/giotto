Why?

The point of giotto is to avoid writing any controllers. All you write is the
model, and the views. Giotto takes care of the rest.

Write our models once, and reuse them across any controller you want!

Example Application:

    def blog_html(blog, errors=None):
        """
        For showing a blog in an http context
        """
        return """<html><body>
                    <h1>{blog.title}</h1>
                    <h2>by {blog.author}</h2>
                    <p>{blog.body}</p>
                  </body></html>""".format(blog=blog)

    def blog_new(blog, errors=None):
        """
        After a blog is created from the command line, return a message
        telling the usser the new blog url 
        """
        url = get_invocation('http', blog.__class__.view, {'id': blog.id})
        return "New blog created! see at %s" % url

    def commandline_blog(blog, errors=None):
        """
        For showing a blog on the commandline.
        """
        if errors:
            return str(errors)
        return "{blog.title}\nby {blog.author}\n\n{blog.body}".format(blog=blog)

    class Blog(models.Model):
        body = models.TextField()
        title = models.CharField(max_length=50)
        author = models.CharField(max_length=50)

        @commandline(blog_new)
        @http(blog_html)
        @classmethod
        def crete_new_blog(cls, title, body, author)
            if len(title) < 50:
                raise ValidationError("title too long")

            return cls.objects.create(title, body, author)

        @commandine(commandline_blog)
        @http(blog_html)
        @classmethod
        def view(self, id)
            blog = self.objects.filter(disabled=False).get(id=id)
            if not blog:
                raise NotFoundError("invalid blog id: %s" % id)
            return blog

Usage:

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
    ('title too long')

    