import unittest
from giotto.exceptions import NoViewMethod
from giotto.views import GiottoView, BasicView, renders
from giotto.control import Redirection

class RendererTests(unittest.TestCase):

    giotto_view = GiottoView()
    basic_view = BasicView()

    def test_mising_renderer(self):
        """
        Exception is raises when you try to render mimetype that is not
        supported by the view class
        """
        assert self.giotto_view.can_render('text/html') == False
        self.assertRaises(NoViewMethod, lambda: self.giotto_view.render({}, 'text/html'))

    def test_render_defined_mimetype(self):
        assert self.basic_view.can_render('text/html') == True
        result = self.basic_view.render({}, 'text/html')
        assert 'body' in result

    def test_kwarg_renderer(self):
        """
        Renderers passed into the constructor override renderers defined on the
        class.
        """
        view = BasicView(html=lambda m: "inherited")
        result = view.render({}, 'text/html')
        self.assertEquals(result['body'], "inherited")

    def test_redirection_lambda(self):
        view = BasicView(html=lambda m: Redirection(m))
        result = view.render('res', 'text/html')
        self.assertEquals(type(result['body']), Redirection)
        self.assertEquals(result['body'].path, 'res')

    def test_redirection(self):
        view = BasicView(html=Redirection('/'))
        result = view.render({}, 'text/html')
        self.assertEquals(type(result['body']), Redirection)

    def test_subclass_renderer(self):
        """
        A Renderer that is defined on a class takes precidence over the renderer
        defined in a base class. Regardless of the name of the render method function.
        """
        class InheritedBasicView1(BasicView):
            @renders('text/html')
            def a(self, result, errors):
                # show up earlier than 'generic_html' in dir()
                return 'inherited'

        class InheritedBasicView2(BasicView):
            @renders('text/html')
            def zzzzzzz(self, result, errors):
                # show up later than 'generic_html' in dir()
                return 'inherited'

        for view in [InheritedBasicView2(), InheritedBasicView1()]:
            result = view.render({}, 'text/html')
            self.assertEquals(result['body'], "inherited")

if __name__ == '__main__':
    unittest.main()