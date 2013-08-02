.. _ref-rendering_templates:

===================
Rendering Templates
===================

Configuring the template engine
-------------------------------

Giotto comes configured to render templates with the Jinja2 library.
In your config file, there should be a variable called ``jinja_env``.
By default, it is configured to look for templates in the root folder of your project.
To change this, modify the path that gets sent into the ``Environment`` constructor.

Rendering Templates
-------------------

Giotto comes with support for rendering jinja template out of the box.
To render a template with a program, add the ``jinja_template`` renderer function to your view class::

    from giotto.programs import Program, Manifest
    from giotto.views import BasicView, jinja_template

    manifest = Manifest({
        'test': Program(
            model=[lambda x,y : {'x': x, 'y':y, 'result': int(x) * int(y)],
            view=BasicView(
                html=jinja_template('mytemplate.html'),
            ),
        ),
    })

In the template, the result of the model will be the only object in the context.
Access ths data by accessing the ``data`` variable::


    <!DOCTYPE html>
    <html>
        {{ data.x }} * {{ data.y }} == {{ data.result }}
    </html>

To change the name of the object in the context, pass in the ``name`` attribute to the renderer::

    BasicView(
        html=jinja_template('mytemplate.html', name="model"),
    )

Partial Template Renderings
---------------------------

Sometimes you want to render a template with multiple data sources.
For instance, you want the view to render the template with data from the model,
but you also want a csrf protection token to be in your template that comes from output middleware.
You can achieve this by using a partial template render::

    from giotto.views import partial_jinja_template

    BasicView(
        html=partial_jinja_template('mytemplate.html'),
    )

If you template looked like this::

    <!DOCTYPE html>
    <html>
        {{ data.x }} * {{ data.y }} == {{ data.result }}<br>
        {{ something_else }}
    </html>

The render would look like this::

    <!DOCTYPE html>
    <html>
        12 * 10 == 120<br>
        {{ something_else }}
    </html>

Since the ``something_else`` variable is undefined, it is ignored by the rendering in the view.
Now your middleware class can parse the body of the response and render it again,
this time with the ``something_else`` variable defined.
