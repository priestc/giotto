import unittest

from giotto.programs import ProgramManifest, GiottoProgram
from giotto.control import Redirection, M

class TestRedirection(unittest.TestCase):

    def test_dot_value(self):
        class Model(object):
            id = 'id'
            title = 'title'
        model = Model()
        r = Redirection('prog', args=[M.id, M.title])
        r.render(model, 'some/mimetype', errors=None)
        self.assertEquals(r.rendered_invocation, ('prog', ['id', 'title'], {}))

    def test_brackets(self):
        model = {'title': 'title', 'id': 'id'} 
        r = Redirection('prog', args=[M['id'], M['title']])
        r.render(model, 'some/mimetype', errors=None)
        self.assertEquals(r.rendered_invocation, ('prog', ['id', 'title'], {}))

    def test_kwargs(self):
        model = {'title': 'title', 'id': 'id'} 
        r = Redirection('prog', kwargs={'id': M['id'], 'title': M['title']})
        r.render(model, 'some/mimetype', errors=None)
        self.assertEquals(r.rendered_invocation, ('prog', [], {'id': 'id', 'title': 'title'}))

if __name__ == '__main__':
    unittest.main()