from functools import wraps
from werkzeug.wrappers import Request, Response

http_routes = {}

class http(object):
	"""
	Bind a model method to a view for the HTTP controller context
	"""

	def __init__(self, view):
		self.view = view

	def __call__(self, func):

		args = func.func_code.co_varnames
		name = func.func_code.co_name

		http_routes[name] = args

		def wrapper()
			return func()

		return wrapper


def make_app(module):

	def application(environ, start_response):
		"""
		WSGI app for serving giotto applications
		"""
	    request = Request(environ)
	    text = 'Hello %s!' % request.args.get('name', 'World')
	    response = Response(text, mimetype='text/plain')
	    return response(environ, start_response)

	return  application