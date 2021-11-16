import sys
if (sys.version_info < (3, 0)):
    raise Exception( 'python3 or bust' )

import os
sys.path.append( os.environ['ezbCTL__ENCLOSING_PROJECT_PATH'] )

import unittest
from easyborrow_controller_code.classes.emailer import Mailer


class MailerTest(unittest.TestCase):

    def setUp(self):
        self.mailer = self.instantiate_mailer()
        pass

    def instantiate_mailer(self):
        """ Sets up Mailer()
            Called by setUp() """
        to_list = [ 'aa', 'bb' ]
        reply_to = 'reply_to'
        subject = 'subject'
        message = 'message'
        request_number = 'request_number'
        mailer = Mailer( to_list, reply_to, subject, message, request_number )
        return mailer

    def tearDown(self):
        pass

    def test_build_mail_to(self):
        # self.assertEqual( [b'aa', b'bb'], self.mailer._build_mail_to() )
        self.assertEqual( ['aa', 'bb'], self.mailer._build_mail_to() )

    ## end class MailerTest()


def suite():
    suite = unittest.TestSuite()
    # suite.addTest( unittest.makeSuite(MailBuilderTest) )
    suite.addTest( unittest.makeSuite(MailerTest) )
    return suite


if __name__ == '__main__':
    unittest.main()
