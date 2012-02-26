import urlparse
from werkzeug.wrappers import Request, Response

class Translator(object):
    @staticmethod
    def feature_from_url(url):
        url = url.split('.')[0]
        model = url.split('/')[1:]
        return ".".join(model)

    @staticmethod
    def format_from_url(url):
        parse = urlparse.urlparse(url)
        format = parse.path.split('.')[1]
        return format
        
    def data_from_request(request):
        if request.method == 'get':
            return request.args
        else:
            return request.data
        
class Handler(object):
    
    def __init__(self, project):
        print "starting wsgi application for %s" % project.project_name
        self.project = __import__(project.project_name)
    
    def dispatch_request(self, request):
        url = request.path
        
        feature = Translator.feature_from_url(url)
        format = Translator.format_from_url(url)
        data = request.data
        
        data = self.project(feature, format, data)
        #data = "Model: %s\nview: %s\ncontroller: %s" % (feature, format, data)
        
        return Response(data)
    
    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

