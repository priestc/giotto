import unittest

from giotto.programs import ProgramManifest, GiottoProgram
from giotto.exceptions import ProgramNotFound

class ExampleProgram1(GiottoProgram):
    pass

class ExampleProgram2(GiottoProgram):
    pass

class ExampleProgram3(GiottoProgram):
    pass

class ExampleProgram4(GiottoProgram):
    pass

class RootProgram(GiottoProgram):
    pass

class ManifestTest(unittest.TestCase):

    manifest = ProgramManifest({
        'prog1': ExampleProgram1(),
        'path1': {
            'prog2': ExampleProgram2(),
            'path2': {
                'prog3': ExampleProgram3(),
                'path3': {
                    '': RootProgram(),
                    'prog4': ExampleProgram4()
                },
            },
        },
    })

    def test_simple_program(self):
        parsed = self.manifest.parse_invocation('prog1.xml')
        self.assertIsInstance(parsed['program'], ExampleProgram1)
        self.assertEquals(parsed['args'], [])
        self.assertEquals(parsed['name'], 'prog1')
        self.assertEquals(parsed['superformat'], 'xml')

    def test_args(self):
        parsed = self.manifest.parse_invocation('prog1.json/arg1/arg2')
        self.assertIsInstance(parsed['program'], ExampleProgram1)
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], 'prog1')
        self.assertEquals(parsed['superformat'], 'json')

    def test_path_and_arg(self):
        parsed = self.manifest.parse_invocation('path1/prog2.html/arg1')
        self.assertIsInstance(parsed['program'], ExampleProgram2)
        self.assertEquals(parsed['args'], ['arg1'])
        self.assertEquals(parsed['name'], 'prog2')
        self.assertEquals(parsed['superformat'], 'html')

    def test_long_path(self):
        parsed = self.manifest.parse_invocation('path1/path2/path3/prog4/arg1/arg2')
        self.assertIsInstance(parsed['program'], ExampleProgram4)
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], 'prog4')
        self.assertEquals(parsed['superformat'], None)

    def test_root(self):
        parsed = self.manifest.parse_invocation('path1/path2/path3/arg1/arg2')
        self.assertIsInstance(parsed['program'], RootProgram)
        self.assertEquals(parsed['args'], ['arg1', 'arg2'])
        self.assertEquals(parsed['name'], '')
        self.assertEquals(parsed['superformat'], None)

    def test_trailing_slash(self):
        parsed = self.manifest.parse_invocation('/prog1/')
        self.assertIsInstance(parsed['program'], ExampleProgram1)
        self.assertEquals(parsed['args'], [])

    def test_not_found(self):
        self.assertRaises(ProgramNotFound, lambda: self.manifest.parse_invocation('path1/path2/fakearg'))

    def test_no_program(self):
        self.assertRaises(ProgramNotFound, lambda: self.manifest.parse_invocation('path1/path2'))

if __name__ == '__main__':
    unittest.main()