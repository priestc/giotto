import unittest
from giotto.exceptions import NoViewMethod
from giotto.views import GiottoView, BasicView

class RendererTest(unittest.TestCase):

    giotto_view = GiottoView()
    basic_view = BasicView()

    def test_mising_renderer(self):
        """
        Exception is raises when you try to render mimetype that is not
        supported by the view class
        """
        assert self.giotto_view.can_render('text/html') == False
        self.assertRaises(NoViewMethod, lambda: self.giotto_view.render({}, 'text/html'))

if __name__ == '__main__':
    unittest.main()