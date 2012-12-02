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

class ManifestTest(unittest.TestCase):

    manifest = ProgramManifest({
        'prog1': ExampleProgram1(),
        'path1': {
            'prog2': ExampleProgram2(),
            'path2': {
                'prog3': ExampleProgram3(),
                'path3': {
                    'prog4': ExampleProgram4()
                },
            },
        },
    })

    def test_simple_program(self):
        program, args = self.manifest.get_program('prog1')
        self.assertIsInstance(program, ExampleProgram1)
        self.assertEquals(args, [])
        self.assertEquals(program.name, 'prog1')
        self.assertEquals(program.path, 'prog1')

    def test_args(self):
        program, args = self.manifest.get_program('prog1/arg1/arg2')
        self.assertIsInstance(program, ExampleProgram1)
        self.assertEquals(args, ['arg1', 'arg2'])
        self.assertEquals(program.name, 'prog1')
        self.assertEquals(program.path, 'prog1')

    def test_path_and_arg(self):
        program, args = self.manifest.get_program('path1/prog2/arg1')
        self.assertIsInstance(program, ExampleProgram2)
        self.assertEquals(args, ['arg1'])
        self.assertEquals(program.name, 'prog2')
        self.assertEquals(program.path, 'path1/prog2')

    def test_long_path(self):
        program, args = self.manifest.get_program('path1/path2/path3/prog4/arg1/arg2')
        self.assertIsInstance(program, ExampleProgram4)
        self.assertEquals(args, ['arg1', 'arg2'])
        self.assertEquals(program.name, 'prog4')
        self.assertEquals(program.path, 'path1/path2/path3/prog4')

    def test_trailing_slash(self):
        program, args = self.manifest.get_program('prog1/')
        self.assertIsInstance(program, ExampleProgram1)
        self.assertEquals(args, [])

    def test_not_found(self):
        self.assertRaises(ProgramNotFound, lambda: self.manifest.get_program('path1/path2/fakearg'))

    def test_no_program(self):
        self.assertRaises(ProgramNotFound, lambda: self.manifest.get_program('path1/path2'))

if __name__ == '__main__':
    unittest.main()