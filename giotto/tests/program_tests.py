import unittest
from collections import OrderedDict

from giotto.programs import GiottoProgram
from giotto.views import BasicView
from giotto.exceptions import MockNotFound

def simple(x, y):
    return None

class ProgramTest(unittest.TestCase):

    def test_no_mock_found(self):
        """
        The program raises MockNotFound when the program has no mock defined
        """
        gp = GiottoProgram(model=[simple])
        self.assertRaises(MockNotFound, lambda: gp.get_model_mock())

    def test_no_mock_needed(self):
        gp = GiottoProgram(model=[])
        self.assertEquals({}, gp.get_model_mock())

    def test_mock_found(self):
        gp = GiottoProgram(model=[simple, {'mock': True}])
        self.assertEquals({'mock': True}, gp.get_model_mock())


class ArgspecTest(unittest.TestCase):
    def test_get_args_kwargs(self):
        def test(a, b, c="what"): pass
        program = GiottoProgram(model=[test], view=BasicView())
        ret = program.get_model_args_kwargs()
        self.assertEquals((['a', 'b'], {'c': "what"}), ret)

    def test_empty(self):
        def test(): pass
        program = GiottoProgram(model=[test], view=BasicView())
        ret = program.get_model_args_kwargs()
        self.assertEquals(([], {}), ret)

    def test_ignore_cls(self):
        """
        If first argument is nammed 'cls', ignore that argument (to allow
        classmethods)
        """
        def test(cls, a, b, c="what"): pass
        program = GiottoProgram(model=[test], view=BasicView())
        ret = program.get_model_args_kwargs()
        self.assertEquals((['a', 'b'], {'c': "what"}), ret)

    def test_no_model(self):
        program = GiottoProgram(view=BasicView())
        ret = program.get_model_args_kwargs()
        self.assertEquals(([], {}), ret)

    def test_preserve_order(self):
        def test(a=1, b=2, c=3, d=4): pass
        program = GiottoProgram(model=[test], view=BasicView())
        a, kw = program.get_model_args_kwargs()
        self.assertEquals(kw.keys(), ['a', 'b', 'c', 'd'])

if __name__ == '__main__':
    unittest.main()