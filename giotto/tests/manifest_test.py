import unittest

from giotto.programs import ProgramManifest, Program
from giotto.exceptions import ProgramNotFound

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

both = Program(name='both', controllers=['irc', 'http-get'])
blank = Program(name='optional_blank')
double_get = Program(name="getter", controllers=['http-get'])
double_post = Program(name="poster", controllers=['http-post'])

class StackedRootTest(unittest.TestCase):
    def setUp(self):
        self.manifest = ProgramManifest({
            '': ProgramManifest({
                '': ProgramManifest({
                    '': Program(name='root'),
                    'deep': Program(name="deep")
                }),
            }),
            'sub': {
                'prog': Program(name="prog"),
                'another': {
                    '': blank,
                    'prog2': Program(name='prog2'),
                    'prog3': Program(name='prog3'),
                    'http_only': Program(name='http_only', controllers=['http-get']),
                    'irc_only': Program(name='irc_only', controllers=['irc']),
                    'both': both
                },
                'double': [double_get, double_post]
            },
            'string_redirect': '/redirect',
            'redirect': Program(name='redirect'),
        })

        self.all_urls = set([
            '/', '/deep',
            '/sub/another/irc_only', '/sub/another/http_only', '/sub/another/both',
            '/sub/prog', '/sub/another', '/sub/another/prog2', '/sub/another/prog3',
            '/redirect', '/string_redirect', '/sub/double'
        ])

        self.irc_only_urls = set(['/sub/another/irc_only'])
        self.http_only_urls = set(['/sub/another/http_only', '/sub/double'])

    def test_get_all_urls(self):
        self.assertEquals(self.manifest.get_urls(), self.all_urls)

    def test_controllertag_filtering(self):
        """
        When a controller tag is added to the call to get_urls, the returned set
        of urls should be filtered by the controler tag defined in the manifest.
        """
        irc_urls = sorted(list(self.all_urls - self.http_only_urls))
        generated = sorted(list(self.manifest.get_urls(controllers=['irc'])))
        self.assertEquals(generated, irc_urls)

        http_urls = self.all_urls - self.irc_only_urls
        self.assertEquals(self.manifest.get_urls(controllers=['http-get']), http_urls)

    def test_get_program(self):
        name = self.manifest.get_program('/').name
        self.assertEquals(name, 'root')

    def test_parse_invocation_simple(self):
        parsed = self.manifest.parse_invocation('/sub/another/both', 'http-get')
        correct = {
            'args': [],
            'program': both,
            'superformat': None,
            'superformat_mime': None,
            'raw_args': '',
            'invocation': '/sub/another/both',
            'path': '/sub/another/',
            'program_name': 'both'
        }
        self.assertEquals(parsed, correct)

    def test_parse_invocation_root_arg(self):
        parsed = self.manifest.parse_invocation('/sub/another/aaaa', 'http-get')
        correct = {
            'args': ['aaaa'],
            'raw_args': 'aaaa',
            'program': blank,
            'superformat': None,
            'superformat_mime': None,
            'invocation': '/sub/another/aaaa',
            'path': '/sub/',
            'program_name': 'another'
        }
        self.assertEquals(parsed, correct)

    def test_parse_invocation_superformat(self):
        parsed = self.manifest.parse_invocation('/sub/another/both.html', 'http-get')
        correct = {
            'args': [],
            'raw_args': '',
            'program': both,
            'superformat': 'html',
            'superformat_mime': 'text/html',
            'invocation': '/sub/another/both.html',
            'path': '/sub/another/',
            'program_name': 'both'
        }
        self.assertEquals(parsed, correct)


    def test_parse_invocation_superformat_with_args(self):
        parsed = self.manifest.parse_invocation('/sub/another/both.html/aaaa/bbbbbb', 'http-get')
        correct = {
            'args': ['aaaa', 'bbbbbb'],
            'raw_args': 'aaaa/bbbbbb',
            'program': both,
            'superformat': 'html',
            'superformat_mime': 'text/html',
            'invocation': '/sub/another/both.html/aaaa/bbbbbb',
            'path': '/sub/another/',
            'program_name': 'both'
        }
        self.assertEquals(parsed, correct)

    def test_parse_invocation_double_controller(self):
        for controller_tag, program in [['http-get', double_get], ['http-post', double_post]]:
            parsed = self.manifest.parse_invocation('/sub/double', controller_tag)
            correct = {
                'args': [],
                'raw_args': '',
                'program': program,
                'superformat': None,
                'superformat_mime': None,
                'invocation': '/sub/double',
                'path': '/sub/',
                'program_name': 'double'
            }
            self.assertEquals(parsed, correct)

    def xtest_parse_invocation_invalid(self):
        #print self.manifest.parse_invocation('/sub/double', 'irc')
        #print self.manifest.get_urls('irc')
        self.assertRaises(
            ProgramNotFound, 
            lambda: self.manifest.parse_invocation('/sub/double', 'irc')
        )

if __name__ == '__main__':
    unittest.main()