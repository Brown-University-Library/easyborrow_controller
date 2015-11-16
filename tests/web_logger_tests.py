# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, json, logging, unittest
from easyborrow_controller_code.classes.web_logger import WebLogger


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s-%(funcName)s()::%(lineno)d - %(message)s')
logger = logging.getLogger('easyborrow_controller')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

wlgr = WebLogger( logger )


class WebLoggerTest(unittest.TestCase):

    def test__run_post(self):
        message = 'test_message'
        identifier = '123'
        self.assertEqual( 200, wlgr.run_post(message, identifier) )

    def test__post_message(self):
        message = 'test_message2'
        identifier = '234'
        importance = 'debug'
        self.assertEqual( 200, wlgr.post_message(message, identifier, importance) )

    def test__evaluate_importance(self):
        wlgr.WEBLOGENTRY_MINIMUM_IMPORTANCE_LEVEL = 'debug'
        self.assertEqual( True, wlgr.evaluate_importance('debug') )
        wlgr.WEBLOGENTRY_MINIMUM_IMPORTANCE_LEVEL = 'info'
        self.assertEqual( False, wlgr.evaluate_importance('debug') )
        wlgr.WEBLOGENTRY_MINIMUM_IMPORTANCE_LEVEL = 'info'
        self.assertEqual( True, wlgr.evaluate_importance('info') )

    # end class WebLoggerTest


if __name__ == "__main__":
    unittest.main()
