import unittest
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict # python2.6

from giotto.programs import Program
from giotto.views import BasicView
from giotto.exceptions import MockNotFound

def simple(x, y):
    return None

class ProgramTest(unittest.TestCase):

    def test_no_mock_found(self):
        """
        The program raises MockNotFound when the program has no mock defined
        """
        gp = Program(model=[simple])
        self.assertRaises(MockNotFound, lambda: gp.get_model_mock())

    def test_no_mock_needed(self):
        gp = Program(model=[])
        self.assertEquals({}, gp.get_model_mock())

    def test_mock_found(self):
        gp = Program(model=[simple, {'mock': True}])
        self.assertEquals({'mock': True}, gp.get_model_mock())


class ArgspecTest(unittest.TestCase):
    def test_get_args_kwargs(self):
        def test(a, b, c="what"): pass
        program = Program(model=[test], view=BasicView())
        ret = program.get_model_args_kwargs()
        self.assertEquals((['a', 'b'], {'c': "what"}), ret)

    def test_empty(self):
        def test(): pass
        program = Program(model=[test], view=BasicView())
        ret = program.get_model_args_kwargs()
        self.assertEquals(([], {}), ret)

    def test_ignore_cls(self):
        """
        If first argument is nammed 'cls', ignore that argument (to allow
        classmethods)
        """
        def test(cls, a, b, c="what"): pass
        program = Program(model=[test], view=BasicView())
        ret = program.get_model_args_kwargs()
        self.assertEquals((['a', 'b'], {'c': "what"}), ret)

    def test_no_model(self):
        program = Program(view=BasicView())
        ret = program.get_model_args_kwargs()
        self.assertEquals(([], {}), ret)

    def test_preserve_order(self):
        def test(a=1, b=2, c=3, d=4): pass
        program = Program(model=[test], view=BasicView())
        a, kw = program.get_model_args_kwargs()
        self.assertEquals(list(kw.keys()), ['a', 'b', 'c', 'd'])

if __name__ == '__main__':
    unittest.main()