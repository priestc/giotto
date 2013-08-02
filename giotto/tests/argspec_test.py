import unittest

from giotto.programs import Program
from giotto.views import GiottoView

class ArgspecTest(unittest.TestCase):

    def test_only_args(self):
        def model(var1, var2): return None
        args, kwargs = Program(model=[model]).get_model_args_kwargs()
        self.assertEquals(args, ['var1', 'var2'])
        self.assertEquals(kwargs, {})

    def test_only_kwargs(self):
        def model(var1=3, var2=9): return None
        args, kwargs = Program(model=[model]).get_model_args_kwargs()
        self.assertEquals(args, [])
        self.assertEquals(kwargs, {'var1': 3, 'var2': 9})

    def test_both(self):
        def model(var0, var1=3, var2=9): return None
        args, kwargs = Program(model=[model]).get_model_args_kwargs()
        self.assertEquals(args, ['var0'])
        self.assertEquals(kwargs, {'var1': 3, 'var2': 9})

    def test_cls_arg(self):
        """
        cls var gets ignored when getting args for a model callable
        """
        class Model(object):
            @classmethod
            def model(cls, var0, var1=3, var2=9):
                return None
        args, kwargs = Program(model=[Model.model]).get_model_args_kwargs()
        self.assertEquals(args, ['var0'])
        self.assertEquals(kwargs, {'var1': 3, 'var2': 9})

if __name__ == '__main__':
    unittest.main()