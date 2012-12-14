import unittest

from giotto.programs import ProgramManifest, GiottoProgram
from giotto.exceptions import ProgramNotFound

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

Base = declarative_base()
class ExampleModel(Base):
    __tablename__ = 'foo'
    id = Column(String, primary_key=True)

    @classmethod
    def example(self):
        return None

class ExampleProgram1(GiottoProgram):
    pass

class ExampleProgram2(GiottoProgram):
    pass

class ExampleProgram3(GiottoProgram):
    model = [ExampleModel.example, {'mock': True}]

class ExampleProgram4(GiottoProgram):
    pass

class RootProgram(GiottoProgram):
    pass

class ControllerTagTest(unittest.TestCase):
    def __init__(self, *a, **k):
        super(ControllerTagTest, self).__init__(*a, **k)
        self.manifest = ProgramManifest({
            '': GiottoProgram(model="root"),
            'prog1': [
                GiottoProgram(model="one", controllers=('get', )),
                GiottoProgram(model="two", controllers=('post', )),
            ]
        })

    def test_one(self):
        parsed = self.manifest.parse_invocation('prog1', 'get')
        self.assertEquals(parsed['program'].model, 'one')
        self.assertEquals(parsed['args'], [])
        self.assertEquals(parsed['name'], 'prog1')
        self.assertEquals(parsed['superformat'], None)

    def test_two(self):
        parsed = self.manifest.parse_invocation('prog1', 'post')
        self.assertEquals(parsed['program'].model, 'two')
        self.assertEquals(parsed['args'], [])
        self.assertEquals(parsed['name'], 'prog1')
        self.assertEquals(parsed['superformat'], None)

class ManifestTest(unittest.TestCase):

    def __init__(self, *a, **k):
        super(ManifestTest, self).__init__(*a, **k)
        self.manifest = ProgramManifest({
            '': GiottoProgram(model="root", controllers=('get', )),
            'prog1': GiottoProgram(model="one", controllers=('get', )),
            'path1': {
                'prog2': GiottoProgram(model="two", controllers=('get', )),
                'path2': {
                    'prog3': GiottoProgram(model="three"),
                    'path3': {
                        '': GiottoProgram(model="root", controllers=('get', )),
                        'prog4': GiottoProgram(model="four", controllers=('get', )),
                    },
                },
            },
        })

    def test_simple_program(self):
        parsed = self.manifest.parse_invocation('prog1.xml', 'get')
        self.assertEquals(parsed['program'].model, 'one')
        self.assertEquals(parsed['args'], [])
        self.assertEquals(parsed['name'], 'prog1')
        self.assertEquals(parsed['superformat'], 'xml')

    def test_args(self):
        parsed = self.manifest.parse_invocation('prog1.json/arg1/arg2', 'get')
        self.assertEquals(parsed['program'].model, "one")
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], 'prog1')
        self.assertEquals(parsed['superformat'], 'json')

    def test_path_and_arg(self):
        parsed = self.manifest.parse_invocation('path1/prog2.html/arg1', 'get')
        self.assertEquals(parsed['program'].model, "two")
        self.assertEquals(parsed['args'], ['arg1'])
        self.assertEquals(parsed['name'], 'prog2')
        self.assertEquals(parsed['superformat'], 'html')

    def test_long_path(self):
        parsed = self.manifest.parse_invocation('path1/path2/path3/prog4/arg1/arg2', 'get')
        self.assertEquals(parsed['program'].model, "four")
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], 'prog4')
        self.assertEquals(parsed['superformat'], None)

    def test_root(self):
        parsed = self.manifest.parse_invocation('path1/path2/path3/arg1/arg2', 'get')
        self.assertEquals(parsed['program'].model, 'root')
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], '')
        self.assertEquals(parsed['superformat'], None)

    def test_trailing_slash(self):
        parsed = self.manifest.parse_invocation('/prog1/', 'get')
        self.assertEquals(parsed['program'].model, 'one')
        self.assertEquals(parsed['args'], [])

    def test_single_root(self):
        parsed = self.manifest.parse_invocation('/', 'get')
        self.assertEquals(parsed['program'].model, 'root')
        self.assertEquals(parsed['args'], [])
        self.assertEquals(parsed['name'], '')
        self.assertEquals(parsed['superformat'], None)

    def test_not_found(self):
        self.assertRaises(ProgramNotFound, lambda: self.manifest.parse_invocation('path1/path2/fakearg', 'get'))

    def test_no_program(self):
        self.assertRaises(ProgramNotFound, lambda: self.manifest.parse_invocation('path1/path2', 'get'))

    def test_no_matching_controller_tag(self):
        self.assertRaises(ProgramNotFound, lambda: self.manifest.parse_invocation('path1/prog2', 'post'))

    def test_every_controller(self):
        """
        If no controller tags are defined for a program, then whitelist all controllers.
        """
        parsed = self.manifest.parse_invocation('/path1/path2/prog3', 'post')
        self.assertEquals(parsed['program'].model, 'three')

class TestNestedBlankManifest(unittest.TestCase):
    def __init__(self, *a, **k):
        super(TestNestedBlankManifest, self).__init__(*a, **k)
        self.nested_blank_manifest = ProgramManifest({
            '': ProgramManifest({
                '': ProgramManifest({
                    '': GiottoProgram(model='root', controllers=('get', )),
                    'prog3': GiottoProgram(model='three'),
                }),
                'prog2': GiottoProgram(model='two', controllers=('get', )),
            }),
            'prog1': GiottoProgram(model='one'),
        })

    def test_lost_superformat(self):
        """
        Superformat is lost when iterative over a blank manifest
        """
        parsed = self.nested_blank_manifest.parse_invocation('/prog2.json/arg1/arg2', 'get')
        self.assertEquals(parsed['program'].model, 'two')
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], 'prog2')
        self.assertEquals(parsed['superformat'], 'json')


    def test_blank(self):
        parsed = self.nested_blank_manifest.parse_invocation('/', 'get')
        self.assertEquals(parsed['program'].model, 'root')
        self.assertEquals(parsed['args'], [])
        self.assertEquals(parsed['name'], '')
        self.assertEquals(parsed['superformat'], None)

    def test_follow(self):
        parsed = self.nested_blank_manifest.parse_invocation('prog2', 'get')
        self.assertEquals(parsed['program'].model, "two")
        self.assertEquals(parsed['args'], [])
        self.assertEquals(parsed['name'], 'prog2')
        self.assertEquals(parsed['superformat'], None)

    def test_follow_with_args(self):
        parsed = self.nested_blank_manifest.parse_invocation('prog2/arg1/arg2', 'get')
        self.assertEquals(parsed['program'].model, 'two')
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], 'prog2')
        self.assertEquals(parsed['superformat'], None)

    def test_root_with_args(self):
        parsed = self.nested_blank_manifest.parse_invocation('/args1/args2', 'get')
        self.assertEquals(parsed['program'].model, 'root')
        self.assertEquals(parsed['args'], ['args1', 'args2'])
        self.assertEquals(parsed['name'], '')
        self.assertEquals(parsed['superformat'], None)

class TestInvalidManifest(unittest.TestCase):

    def test_invalid_key(self):
        x = lambda: ProgramManifest({'invalid.key': GiottoProgram()})
        self.assertRaises(ValueError, x)

    def test_invalid_program_type(self):
        x = lambda: ProgramManifest({'xx': "not a program"})
        self.assertRaises(TypeError, x)

if __name__ == '__main__':
    unittest.main()