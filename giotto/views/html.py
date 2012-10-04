import json

def make_html_renderer(jinja_env):
    """
    Create an HTML renderer bound to a project's settings for a jinja enviornment
    """
    class HTML(object):
        """
        Lazy evaluation of html documents.
        """
        def __init__(self, template, mimetype='text/html'):
            self.template = template
            self.mimetype = mimetype

        def render(self, model, errors={}, input={}):
            """
            Render the template, and return as a string.
            """
            template = jinja_env.get_template(self.template)
            content = template.render(errors=errors, input={}, obj=model)
            return {'response': content, 'mimetype': self.mimetype}

    return HTML

class JSON(object):
    """
    Wrapper for rendering JSON objects
    """
    @classmethod
    def render(cls, model):
        try:
            j = json.dumps(model)
        except TypeError:
            j = json.dumps(model.__dict__)

        return {'response': j, "mimetype": "application/json"}