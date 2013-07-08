import unittest

from giotto.programs import ProgramManifest, GiottoProgram
from giotto.exceptions import ProgramNotFound

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

both = GiottoProgram(name='both', controllers=['irc', 'http-get'])
blank = GiottoProgram(name='optional_blank')

class StackedRootTest(unittest.TestCase):
    def setUp(self):
        self.manifest = ProgramManifest({
            '': ProgramManifest({
                '': ProgramManifest({
                    '': GiottoProgram(name='root'),
                    'deep': GiottoProgram(name="deep")
                }),
            }),
            'sub': {
                'prog': GiottoProgram(name="prog"),
                'another': {
                    '': blank,
                    'prog2': GiottoProgram(name='prog2'),
                    'prog3': GiottoProgram(name='prog3'),
                    'http_only': GiottoProgram(name='http_only', controllers=['http-get']),
                    'irc_only': GiottoProgram(name='irc_only', controllers=['irc']),
                    'both': both
                }
            },
            'string_redirect': '/redirect',
            'redirect': GiottoProgram(name='redirect'),
        })

        self.all_urls = set([
            '/', '/deep',
            '/sub/another/irc_only', '/sub/another/http_only', '/sub/another/both',
            '/sub/prog', '/sub/another', '/sub/another/prog2', '/sub/another/prog3',
            '/redirect', '/string_redirect',
        ])

        self.irc_only_urls = set(['/sub/another/irc_only'])
        self.http_only_urls = set(['/sub/another/http_only'])

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
            'invocation': '/sub/another/both',
            'path': '/sub/another/',
            'program_name': 'both'
        }
        self.assertEquals(parsed, correct)

    def test_parse_invocation_root_arg(self):
        parsed = self.manifest.parse_invocation('/sub/another/fart', 'http-get')
        correct = {
            'args': ['fart'],
            'program': blank,
            'superformat': None,
            'invocation': '/sub/another/fart',
            'path': '/sub/',
            'program_name': 'another'
        }
        self.assertEquals(parsed, correct)

    def xtest_parse_invocation_superformat(self):
        parsed = self.manifest.parse_invocation('/sub/another/both.html', 'http-get')
        correct = {
            'args': ['fart'],
            'program': blank,
            'superformat': 'html',
            'invocation': '/sub/another/fart',
            'path': '/sub/',
            'program_name': 'another'
        }
        self.assertEquals(parsed, correct)


if __name__ == '__main__':
    unittest.main()