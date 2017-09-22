# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest
from easyborrow_controller_code.classes.emailer import Mailer


# class MailBuilderTest(unittest.TestCase):

#     def setUp(self):
#         self.builder = self.instantiate_mail_builder()
#         pass

#     def instantiate_mail_builder(self):
#         ( request_inst, patron_inst, item_inst ) = ( 'x', 'y', 'z' )
#         builder = MailBuilder( request_inst, patron_inst, item_inst )
#         return builder

#     def tearDown(self):
#         pass

#     def test_build_to(self):
#         self.assertEqual( 'foo1', self.builder.build_to() )

#     ## end class MailBuilderTest()


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
        self.assertEqual( ['aa', 'bb'], self.mailer._build_mail_to() )

    ## end class MailerTest()


def suite():
    suite = unittest.TestSuite()
    # suite.addTest( unittest.makeSuite(MailBuilderTest) )
    suite.addTest( unittest.makeSuite(MailerTest) )
    return suite


if __name__ == '__main__':
    unittest.main()
