import unittest
import json

from giotto import initialize
from giotto.controllers.http import HTTPController
from giotto.programs import GiottoProgram, ProgramManifest
from giotto.exceptions import ProgramNotFound
from giotto.primitives import LOGGED_IN_USER, RAW_INVOCATION_ARGS
from giotto.views import BasicView

from webob import Request

def make_request(path):
	r = Request.blank(path)
	r.user = "My User"
	return r

def no_defaults(x, y):
	return int(x) * int(y)

def defaults(x=4, y=2):
	return int(x) * int(y)

def primitive(x=LOGGED_IN_USER):
	return int(x) * int(y)

def raw(path=RAW_INVOCATION_ARGS, another=3):
	return path + str(another)

def none(x=None, y=None):
	return "%s %s" % (x, y)

def order(a='a', b='b', c='c', d='d', e='e', f='f', g='g'):
	return [a, b, c, d, e, f, g]

class NegotiationTest(unittest.TestCase):

	def setUp(self):
		initialize()
		self.manifest = ProgramManifest({
			'no_defaults': GiottoProgram(
				model=[no_defaults],
				view=BasicView()
			),
			'defaults': GiottoProgram(
				model=[defaults],
				view=BasicView()
			),
			'primitives': GiottoProgram(
				model=[primitive],
				view=BasicView()
			),
			'raw': GiottoProgram(
				model=[raw],
				view=BasicView()
			),
			'none': GiottoProgram(
				model=[none],
				view=BasicView
			),
			'order': GiottoProgram(
				model=[order],
				view=BasicView
			)
		})

	def test_args(self):
		request = make_request("/no_defaults.json/3/5")
		c = HTTPController(request, self.manifest)
		data = c.get_data_response()
		self.assertEquals(json.loads(data['body']), 15)

	def test_kwargs(self):
		request = make_request("/no_defaults.json?x=3&y=4")
		c = HTTPController(request, self.manifest)
		data = c.get_data_response()
		self.assertEquals(json.loads(data['body']), 12)

	def test_mixed(self):
		request = make_request("/no_defaults.json/5?y=4")
		c = HTTPController(request, self.manifest)
		data = c.get_data_response()
		self.assertEquals(json.loads(data['body']), 20)

	def test_default(self):
		request = make_request("/defaults.json")
		c = HTTPController(request, self.manifest)
		data = c.get_data_response()
		self.assertEquals(json.loads(data['body']), 8)

	def test_order(self):
		request = make_request("/order.json/1/2/3/4/5/6/7")
		c = HTTPController(request, self.manifest)
		data = c.get_data_response()
		self.assertEquals(json.loads(data['body']), ['1', '2', '3', '4', '5', '6', '7'])

	def test_order_defaults(self):
		request = make_request("/order.json")
		c = HTTPController(request, self.manifest)
		data = c.get_data_response()
		self.assertEquals(json.loads(data['body']), ['a', 'b', 'c', 'd', 'e', 'f', 'g'])

	def test_none(self):
		request = make_request("/none.json/3")
		c = HTTPController(request, self.manifest)
		data = c.get_data_response()
		self.assertEquals(json.loads(data['body']), "3 None")

	def test_missing(self):
		"""
		Exception is raised when data arguments are missing when invoking a program.
		"""
		request = make_request("/no_defaults.json/5")
		c = HTTPController(request, self.manifest)
		self.assertRaises(Exception, c.get_data_response)

	def test_too_much_data(self):
		"""
		Exception is raised when too many data arguments are passed into a program.
		"""
		request = make_request("/no_defaults.json/5/12/2")
		c = HTTPController(request, self.manifest)
		self.assertRaises(Exception, c.get_data_response)

	def test_raw_primitive(self):
		request = make_request("/raw.json/raw/arg/to_some/program")
		c = HTTPController(request, self.manifest)
		data = c.get_data_response()
		self.assertEquals(json.loads(data['body']), "raw/arg/to_some/program3")