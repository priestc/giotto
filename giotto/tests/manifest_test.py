import unittest

from giotto.programs import ProgramManifest, GiottoProgram
from giotto.exceptions import ProgramNotFound

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

class StackedRootTest(unittest.TestCase):
    def setUp(self):
        self.manifest = ProgramManifest({
            '': ProgramManifest({
                '': ProgramManifest({
                    '': GiottoProgram(model='root'),
                    'deep': GiottoProgram(model="deep")
                }),
            }),
            'sub': {
                'prog': GiottoProgram(model="prog"),
                'another': {
                    '': GiottoProgram(model='optional_blank'),
                    'prog2': GiottoProgram(model='prog2'),
                    'prog3': GiottoProgram(model='prog3'),
                    'http_only': GiottoProgram(model='http_only', controller_tags=['http-get']),
                    'irc_only': GiottoProgram(model='irc_only', controller_tag=['irc'])
                }
            },
            'string_redirect': '/redirect',
            'redirect': GiottoProgram(model='redirect'),
        })

        self.all_urls = {
            '/', '/deep',
            '/sub/another/irc_only', '/sub/another/http_only',
            '/sub/prog', '/sub/another', '/sub/another/prog2', '/sub/another/prog3',
            '/redirect', '/string_redirect',
        }

        self.irc_only_urls = {'/sub/another/irc_only'}
        self.http_only_urls = {'/sub/another/http_only'}

    def test_get_all_urls(self):
        self.assertEquals(self.manifest.get_urls(), self.all_urls)

    def test_controllertag_filtering(self):
        """
        When a controller tag is added to the call to get_urls, the returned set
        of urls should be filtered by the controler tag defined in the manifest.
        """
        irc_urls = self.all_urls - self.http_only_urls
        self.assertEquals(self.manifest.get_urls(controller_tags=['irc']), irc_urls)

        http_urls = self.all_urls - self.irc_only_urls
        #self.assertEquals(self.manifest.get_urls(controller_tags=['http-get']), http_urls)

    def test_get_program(self):
        model = self.manifest.get_program('/').model
        self.assertEquals(model, 'root')

if __name__ == '__main__':
    unittest.main()