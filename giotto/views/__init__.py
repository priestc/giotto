from jinja2 import Template
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
            return {'body': content, 'mimetype': self.mimetype}

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

class TEXT(object):
    def __init__(self, text, mimetype='text/plain'):
        self.text = text
        self.mimetype = mimetype

    def render(self, model):
        """
        Render the template, and return as a string.
        """
        template = Template(self.text)
        content = template.render(obj=model)
        return {'body': content, 'mimetype': self.mimetype}