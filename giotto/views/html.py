from giotto.core import config

class HTML(object):
    """
    Lazy evaluation of html documents.
    """
    def __init__(self, template, mimetype='text/html'):
        self.template = template
        self.mimetype = mimetype

    def __call__(self, context):
        """
        Render the template, and return as a string.
        """
        import debug
        env = config.jinja2_env
        template = env.get_template(self.template)
        return template.render(**context)
