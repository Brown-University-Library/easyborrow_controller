# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, json, unittest
from easyborrow_controller_code.classes.tunneler_runners import IlliadApiRunner
from easyborrow_controller_code.classes.basics import Request_Meta


class IlliadApiRunnerTest(unittest.TestCase):

    def setUp(self):
        self.illiad_runner = self.instantiate_illiad_runner()
        pass

    def instantiate_illiad_runner(self):
        """ Sets up IlliadApiRunner instance.
            Called by setUp() """
        request_instance = Request_Meta()
        request_instance.request_number = 42
        illiad_runner = IlliadApiRunner( request_instance )
        return illiad_runner

    def tearDown(self):
        pass

    def test_make_openurl_segment__simple_case(self):
        volumes_info = ''
        initial_url = 'http://rl3tp7zf5x.search.serialssolutions.com/?sid=test&genre=book&isbn=9780439339117'
        self.assertEqual( 'sid=test&genre=book&isbn=9780439339117', self.illiad_runner._make_openurl_segment(initial_url, volumes_info) )

    def test_make_openurl_segment__unknown_genre(self):
        volumes_info = ''
        initial_url = 'http://rl3tp7zf5x.search.serialssolutions.com/?sid=test&genre=unknown&isbn=9780439339117'
        self.assertEqual( 'sid=test&genre=book&isbn=9780439339117', self.illiad_runner._make_openurl_segment(initial_url, volumes_info) )

    def test_make_openurl_segment__volume_note(self):
        volumes_info = 'test note'
        initial_url = 'http://rl3tp7zf5x.search.serialssolutions.com/?sid=test&genre=unknown&isbn=9780439339117'
        self.assertEqual( 'sid=test&genre=book&isbn=9780439339117&notes=test+note', self.illiad_runner._make_openurl_segment(initial_url, volumes_info) )

    def test_make_openurl_segment__unicode_volume_note(self):
        volumes_info = 'tést note'
        initial_url = 'http://rl3tp7zf5x.search.serialssolutions.com/?sid=test&genre=unknown&isbn=9780439339117'
        self.assertEqual( 'sid=test&genre=book&isbn=9780439339117&notes=t%C3%A9st+note', self.illiad_runner._make_openurl_segment(initial_url, volumes_info) )

    ## end class IlliadApiRunnerTest()


def suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(IlliadApiRunnerTest) )
    return suite


if __name__ == '__main__':
    unittest.main()
