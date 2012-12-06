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

class ManifestTest(unittest.TestCase):

    def __init__(self, *a, **k):
        super(ManifestTest, self).__init__(*a, **k)
        self.manifest = ProgramManifest({
            '': RootProgram,
            'prog1': ExampleProgram1,
            'path1': {
                'prog2': ExampleProgram2,
                'path2': {
                    'prog3': ExampleProgram3,
                    'path3': {
                        '': RootProgram,
                        'prog4': ExampleProgram4
                    },
                },
            },
        })

    def test_simple_program(self):
        parsed = self.manifest.parse_invocation('prog1.xml')
        self.assertEquals(parsed['program'], ExampleProgram1)
        self.assertEquals(parsed['args'], [])
        self.assertEquals(parsed['name'], 'prog1')
        self.assertEquals(parsed['superformat'], 'xml')

    def test_args(self):
        parsed = self.manifest.parse_invocation('prog1.json/arg1/arg2')
        self.assertEquals(parsed['program'], ExampleProgram1)
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], 'prog1')
        self.assertEquals(parsed['superformat'], 'json')

    def test_path_and_arg(self):
        parsed = self.manifest.parse_invocation('path1/prog2.html/arg1')
        self.assertEquals(parsed['program'], ExampleProgram2)
        self.assertEquals(parsed['args'], ['arg1'])
        self.assertEquals(parsed['name'], 'prog2')
        self.assertEquals(parsed['superformat'], 'html')

    def test_long_path(self):
        parsed = self.manifest.parse_invocation('path1/path2/path3/prog4/arg1/arg2')
        self.assertEquals(parsed['program'], ExampleProgram4)
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], 'prog4')
        self.assertEquals(parsed['superformat'], None)

    def test_root(self):
        parsed = self.manifest.parse_invocation('path1/path2/path3/arg1/arg2')
        self.assertEquals(parsed['program'], RootProgram)
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], '')
        self.assertEquals(parsed['superformat'], None)

    def test_trailing_slash(self):
        parsed = self.manifest.parse_invocation('/prog1/')
        self.assertEquals(parsed['program'], ExampleProgram1)
        self.assertEquals(parsed['args'], [])

    def test_single_root(self):
        parsed = self.manifest.parse_invocation('/')
        self.assertEquals(parsed['program'], RootProgram)
        self.assertEquals(parsed['args'], [])
        self.assertEquals(parsed['name'], '')
        self.assertEquals(parsed['superformat'], None)

    def test_not_found(self):
        self.assertRaises(ProgramNotFound, lambda: self.manifest.parse_invocation('path1/path2/fakearg'))

    def test_no_program(self):
        self.assertRaises(ProgramNotFound, lambda: self.manifest.parse_invocation('path1/path2'))

    def test_program_finder(self):
        progs = {ExampleProgram1, ExampleProgram2, ExampleProgram3, ExampleProgram4, RootProgram}
        self.assertEquals(self.manifest.get_all_programs(), progs)


class TestNestedBlankManifest(unittest.TestCase):
    def __init__(self, *a, **k):
        super(TestNestedBlankManifest, self).__init__(*a, **k)
        self.nested_blank_manifest = ProgramManifest({
            '': ProgramManifest({
                '': ProgramManifest({
                    '': RootProgram,
                    'prog3': ExampleProgram3,
                }),
                'prog2': ExampleProgram2,
            }),
            'prog1': ExampleProgram1,
        })

    def test_blank(self):
        parsed = self.nested_blank_manifest.parse_invocation('/')
        self.assertEquals(parsed['program'], RootProgram)
        self.assertEquals(parsed['args'], [])
        self.assertEquals(parsed['name'], '')
        self.assertEquals(parsed['superformat'], None)

    def test_follow(self):
        parsed = self.nested_blank_manifest.parse_invocation('prog2')
        self.assertEquals(parsed['program'], ExampleProgram2)
        self.assertEquals(parsed['args'], [])
        self.assertEquals(parsed['name'], 'prog2')
        self.assertEquals(parsed['superformat'], None)

    def test_follow_with_args(self):
        parsed = self.nested_blank_manifest.parse_invocation('prog2/arg1/arg2')
        self.assertEquals(parsed['program'], ExampleProgram2)
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], 'prog2')
        self.assertEquals(parsed['superformat'], None)

    def test_root_with_args(self):
        parsed = self.nested_blank_manifest.parse_invocation('/args1/args2')
        self.assertEquals(parsed['program'], RootProgram)
        self.assertEquals(parsed['args'], ['args1', 'args2'])
        self.assertEquals(parsed['name'], '')
        self.assertEquals(parsed['superformat'], None)

class TestInvalidManifest(unittest.TestCase):

    def test_invalid_key(self):
        x = lambda: ProgramManifest({'invalid.key': RootProgram})
        self.assertRaises(ValueError, x)

    def test_invalid_program_type(self):
        x = lambda: ProgramManifest({'xx': "not a program"})
        self.assertRaises(TypeError, x)

if __name__ == '__main__':
    unittest.main()