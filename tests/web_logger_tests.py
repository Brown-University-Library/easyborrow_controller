# -*- coding: utf-8 -*-

import datetime, json, logging, unittest
from easyborrow_controller_code.classes.web_logger import WebLogger


formatter = logging.Formatter(u'%(asctime)s - %(levelname)s - %(module)s-%(funcName)s()::%(lineno)d - %(message)s')
logger = logging.getLogger('easyborrow_controller')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

wlgr = WebLogger( logger )


class WebLoggerTest(unittest.TestCase):

    def test__run_post(self):
        message = u'test_message'
        identifier = u'123'
        self.assertEqual( 200, wlgr.run_post(message, identifier) )

    def test__post_message(self):
        message = u'test_message2'
        identifier = u'234'
        importance = u'debug'
        self.assertEqual( 200, wlgr.post_message(message, identifier, importance) )

    # end class WebLoggerTest


if __name__ == "__main__":
    unittest.main()
