class GiottoOutputMiddleware(object):
    def __init__(self, controller):
        self.controller = controller

class GiottoInputMiddleware(object):
    def __init__(self, controller):
        self.controller = controller

class RenderLazytemplate(GiottoOutputMiddleware):
    def http(self, request, response):
        engine, template, context = response.lazy_data
        if engine == 'jinja2':
            rendered = template.render(**context)
        response.data = rendered
        return response