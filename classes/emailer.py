# -*- coding: utf-8 -*-

""" Unicode-friendly emailer.
    Called by EzBorrowController.py """

from __future__ import unicode_literals

import json, logging, os, pprint, smtplib
from email.Header import Header
from email.mime.text import MIMEText
from easyborrow_controller_code import settings
from easyborrow_controller_code.classes.web_logger import WebLogger


log = logging.getLogger(__name__)


class MailBuilder( object ):
    """ Preps email that'll be send by Mailer() """

    def __init__( self, request_inst, patron_inst, item_inst ):
        self.request_inst = request_inst  # instance-object (holds request_number, service, status, and reference_number)
        self.patron_inst = patron_inst  # instance-object
        self.item_inst = item_inst  # instance-object
        self.to = []
        self.apparent_sender = 'brown_library_easyborrow_system'
        self.reply_to = ''
        self.subject = "Subject: Update on your 'easyBorrow' request"
        self.message = ''

    def prep_email( self ):
        """ Preps variable email fields.
            Called by controller. """
        self.build_to()
        self.build_reply_to()
        self.build_message()
        return

    def build_to( self ):
        """ Preps `to` data.
            Called by prep_email() """
        if self.request_inst.current_status == 'error':
            self.to = [ settings.ADMIN_EMAIL ]
        elif self.request_inst.current_service == 'borrowDirect':
            self.to = [ self.patron_inst.email ]
        elif self.request_inst.current_service == 'illiad':
            self.to = [ self.patron_inst.email ]
        return

    def build_reply_to( self ):
        """ Preps `reply_to` data.
            Called by prep_email() """
        if self.request_inst.current_status == 'error':
            self.reply_to = ''
        elif self.request_inst.current_service == 'borrowDirect':
            self.reply_to = 'rock@brown.edu'
        elif self.request_inst.current_service == 'illiad':
            self.reply_to = 'interlibrary_loan@brown.edu'
        return

    def build_message( self ):
        """ Preps `message` data.
            Called by prep_email() """
        if self.request_inst.current_status == 'error':
            self.message = 'BJD - handle this situation.'
        elif self.request_inst.current_service == 'borrowDirect':
            self.message = self.make_borrowdirect_message()
        elif self.request_inst.current_service == 'illiad' and self.request_inst.current_status == 'success':
            self.message = self.make_illiad_success_message()
        elif self.request_inst.current_service == 'illiad' and self.request_inst.current_status == 'login_failed_possibly_blocked':
            self.message = self.make_illiad_blocked_message()
        return

    def make_borrowdirect_message( self ):
        """ Preps borrowdirect message.
            Called by build_message() """
        message = '''
Greetings %s %s,

We've located the title '%s' and have ordered it for you. You'll be notified when it arrives.

Some useful information for your records:

- Title: '%s'
- Your 'easyBorrow' reference number: '%s'
- Ordered from service: 'BorrowDirect'
- Your BorrowDirect reference number: '%s'
- Notification of arrival will be sent to email address: '%s'

If you have any questions, contact the Library's Rockefeller Gateway staff at rock@brown.edu or call 401-863-2165.

    ''' % (
        self.patron_inst.firstname,
        self.patron_inst.lastname,
        self.item_inst.title,
        self.item_inst.title,
        self.request_inst.request_number,
        self.request_inst.confirmation_code,
        self.patron_inst.email )
        return message
        ####### end make_borrowdirect_message() #######

    def make_illiad_success_message( self ):
        """ Preps illiad success message.
            Called by build_message() """
        message = '''
Greetings %s %s,

We've located the title '%s' and have ordered it for you. You'll be notified when it arrives.

Some useful information for your records:

- Title: '%s'
- Your 'easyBorrow' reference number: '%s'
- Ordered from service: 'Illiad'
- Your Illiad reference number: '%s'
- Notification of arrival will be sent to email address: '%s'

You can check your Illiad account at the link:
<https://illiad.brown.edu/illiad/>

If you have any questions, contact the Library's Interlibrary Loan office at interlibrary_loan@brown.edu or call 863-2169.

  ''' % (
        self.patron_inst.firstname,
        self.patron_inst.lastname,
        self.item_inst.title,
        self.item_inst.title,
        self.request_inst.request_number,
        self.request_inst.confirmation_code,
        self.patron_inst.email )
        return message
        ###### end make_illiad_success_message() ######

    def make_illiad_blocked_message( self ):
        """ Preps illiad blocked message.
            Called by build_message() """
        message = '''
Greetings %s %s,

Your request for the item, '%s', could not be fulfilled by our easyBorrow service. It appears there is a problem with your Interlibrary Loan, ILLiad account.

Contact the Interlibrary Loan office at the email address above or at 401/863-2169. The staff will work with you to resolve the problem.

Once your account issue is cleared up, click on this link to re-request the item:
<%s>

( easyBorrow request reference number: '%s' )

[end]
    ''' % (
        self.patron_inst.firstname,
        self.patron_inst.lastname,
        self.item_inst.title,
        'http://worldcat.org/oclc/%s' % self.item_inst.oclc_number,
        self.request_inst.request_number )
        return message
        ####### end make_illiad_blocked_message() #######

    # end class MailBuilder


class Mailer( object ):
    """ Specs email handling. """

    def __init__( self, to_list, reply_to, subject, message, request_number ):
        self.SMTP_SERVER = settings.MAIL_SMTP_SERVER
        self.TO_LIST = to_list  # eg: [ 'addr1@domain.edu', 'addr2@domain.com' ]
        self.FROM_REAL = settings.MAIL_SENDER  # real 'from' unicode-string address smtp server will user, eg: 'addr3@domain.edu'
        self.FROM_HEADER = settings.MAIL_APPARENT_SENDER  # apparent 'from' unicode-string user will see, eg: 'some_system'
        self.REPLY_TO_HEADER = reply_to  # unicode-string
        self.SUBJECT = subject  # unicode-string
        self.MESSAGE = message  # unicode-string
        self.request_number = request_number  # unicode-string
        log.debug( '%s - Mailer instantiated' % self.request_number )

    def send_email( self ):
        """ Sends email. """
        try:
            TO = self._build_mail_to()  # list of utf-8 entries
            MESSAGE = self.MESSAGE.encode( 'utf-8', 'replace' )
            payload = self._assemble_payload( TO, MESSAGE )
            s = smtplib.SMTP( self.SMTP_SERVER.encode('utf-8', 'replace') )
            s.sendmail( self.FROM_REAL.encode('utf-8', 'replace'), TO.encode('utf-8', 'replace'), payload.as_string() )
            s.quit()
            log.debug( 'mail sent' )
            return True
        except Exception as e:
            log.error( 'problem sending mail, exception, `%s`' % unicode(repr(e)) )
            return False

    def _build_mail_to( self ):
        """ Builds and returns 'to' list of email addresses.
            Called by send_email() """
        utf8_to_list = []
        for address in self.TO_LIST:
            utf8_to_list.append( address.encode('utf-8', 'replace') )
        return utf8_to_list

    def _assemble_payload( self, TO, MESSAGE ):
        """ Puts together and returns email payload.
            Called by send_email(). """
        payload = MIMEText( MESSAGE )
        payload['To'] = ', '.join( TO.encode('utf-8', 'replace') )
        payload['From'] = self.FROM_HEADER.encode( 'utf-8', 'replace' )
        payload['Subject'] = Header( self.SUBJECT, 'utf-8' )  # Header handles encoding
        payload['Reply-to'] = self.REPLY_TO_HEADER.encode( 'utf-8', 'replace' )
        return payload

    # end class Mailer


# class Mailer( object ):
#     """ Specs email handling. """

#     def __init__( self, to_json, reply_to, UNICODE_SUBJECT, UNICODE_MESSAGE, request_number ):
#         self.UTF8_SMTP_SERVER = settings.MAIL_SMTP_SERVER
#         self.UTF8_RAW_TO_JSON = to_json  # json (ensures reliable formatting/encoding), eg: '["addr1@domain.edu", "addr2@domain.com"]'
#         self.UTF8_FROM_REAL = settings.MAIL_SENDER  # real 'from' address smtp server will user, eg: 'addr3@domain.edu'
#         self.UTF8_FROM_HEADER = settings.MAIL_APPARENT_SENDER  # apparent 'from' string user will see, eg: 'some_system'
#         self.UTF8_REPLY_TO_HEADER = reply_to
#         self.UNICODE_SUBJECT = UNICODE_SUBJECT
#         self.UNICODE_MESSAGE = UNICODE_MESSAGE
#         self.request_number = request_number
#         log.debug( '%s - Mailer instantiated' % self.request_number )

#     def send_email( self ):
#         """ Sends email. """
#         try:
#             TO = self._build_mail_to()  # list of utf-8 entries
#             MESSAGE = self.UNICODE_MESSAGE.encode( 'utf-8', 'replace' )  # utf-8
#             payload = self._assemble_payload( TO, MESSAGE )
#             s = smtplib.SMTP( self.UTF8_SMTP_SERVER )
#             s.sendmail( self.UTF8_FROM_REAL, TO, payload.as_string() )
#             s.quit()
#             log.debug( 'mail sent' )
#             return True
#         except Exception as e:
#             log.error( 'problem sending mail, exception, `%s`' % unicode(repr(e)) )
#             return False

#     def _build_mail_to( self ):
#         """ Builds and returns 'to' list of email addresses.
#             Called by send_email() """
#         to_emails = json.loads( self.UTF8_RAW_TO_JSON )
#         utf8_to_list = []
#         for address in to_emails:
#             utf8_to_list.append( address.encode('utf-8') )
#         return utf8_to_list

#     def _assemble_payload( self, TO, MESSAGE ):
#         """ Puts together and returns email payload.
#             Called by send_email(). """
#         payload = MIMEText( MESSAGE )
#         payload['To'] = ', '.join( TO )
#         payload['From'] = self.UTF8_FROM_HEADER
#         payload['Subject'] = Header( self.UNICODE_SUBJECT, 'utf-8' )  # subject must be unicode
#         payload['Reply-to'] = self.UTF8_REPLY_TO_HEADER
#         return payload

#     # end class Mailer
