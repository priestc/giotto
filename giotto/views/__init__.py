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

class GiottoView(object):
    def __init__(self, result):
        """
        result == the output from the model
        """
        self.result = result

    def render(self, mimetype):
        method = mimetype.replace('/', '_')
        renderer = getattr(self, method)
        data = renderer(self.result)
        return {'body': data, 'mimetype': mimetype}

class GiottoTemplateView(GiottoView):
    """
    A view renderer where each mimetype renderer returns a jinja template that
    will get rendered automatically. The context_name attribute denotes the
    name of the model object in the template.
    """
    context_name = 'obj'
    def render(self, mimetype):
        result = super(GiottoTemplateView, self).render(mimetype)
        template = result['body']
        if hasattr(template, 'lower'):
            jinja_template = Template(template)
            rendered = jinja_template.render(obj=self.result)
            result['body'] = rendered
            return result
        raise TypeError('Template must be a string')


