# -*- coding: utf-8 -*-

import datetime, json, logging, unittest
from easyborrow_controller_code.classes import db_handler


formatter = logging.Formatter(u'%(asctime)s - %(levelname)s - %(module)s-%(funcName)s()::%(lineno)d - %(message)s')
logger = logging.getLogger('easyborrow_controller')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

dbh = db_handler.Db_Handler( logger )


class Db_HandlerTest(unittest.TestCase):

  def test__unicodify_resultset(self):
    dict_list = [ {'title': 'réd' } ]
    self.assertNotEqual( [ {'title': 'réd' } ], dbh._unicodify_resultset(dict_list) )
    self.assertEqual( [ {u'title': u'réd' } ], dbh._unicodify_resultset(dict_list) )




if __name__ == "__main__":
  unittest.main()
