# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, json, logging, unittest
from easyborrow_controller_code.classes import db_handler


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s-%(funcName)s()::%(lineno)d - %(message)s')
logger = logging.getLogger('easyborrow_controller')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

dbh = db_handler.Db_Handler( logger )


class Db_HandlerTest(unittest.TestCase):

    def test__unicodify_resultset_unicode(self):
        dict_list = [ {'title': 'réd' } ]
        self.assertNotEqual( [ {'title': 'réd' } ], dbh._unicodify_resultset(dict_list) )
        self.assertEqual( [ {'title': 'réd' } ], dbh._unicodify_resultset(dict_list) )

    def test__unicodify_resultset_unicode(self):
        dict_list = [ {'title': 'réd', 'wc': long( 123 ) } ]
        self.assertEqual( [ {'title': 'réd', 'wc': '123' } ], dbh._unicodify_resultset(dict_list) )





if __name__ == "__main__":
    unittest.main()
