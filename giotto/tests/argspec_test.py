import unittest

from giotto.programs import GiottoProgram
from giotto.views import GiottoView

def make_program(model):
    model_ = model

    class SomeView(GiottoView):
        def text_html(result):
            return result

    class ExampleProgram(GiottoProgram):
        model = [model_]
        view = SomeView
    return ExampleProgram

class ArgspecTest(unittest.TestCase):

    def test_only_args(self):
        def model(var1, var2): return None
        args, kwargs = make_program(model).get_model_args_kwargs()
        self.assertEquals(args, ['var1', 'var2'])
        self.assertEquals(kwargs, {})

    def test_only_kwargs(self):
        def model(var1=3, var2=9): return None
        args, kwargs = make_program(model).get_model_args_kwargs()
        self.assertEquals(args, [])
        self.assertEquals(kwargs, {'var1': 3, 'var2': 9})

    def test_both(self):
        def model(var0, var1=3, var2=9): return None
        args, kwargs = make_program(model).get_model_args_kwargs()
        self.assertEquals(args, ['var0'])
        self.assertEquals(kwargs, {'var1': 3, 'var2': 9})   

if __name__ == '__main__':
    unittest.main()