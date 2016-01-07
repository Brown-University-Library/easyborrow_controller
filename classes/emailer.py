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

    def __init__( self, patron, item, log_identifier ):
        self.patron = patron
        self.item = item
        self.log_identifier = log_identifier
        self.to = []
        self.apparent_sender = ''
        self.reply_to = ''
        self.subject = "Subject: Update on your 'easyBorrow' request"
        self.message = ''

    def prep_email( self, service, status ):
        """ Preps variable email fields.
            Called by controller. """
        if service == 'borrowDirect' and status == 'success':
            self.to = [ patron.email ]
            self.apparent_sender = 'Reply-To: rock@brown.edu'
        elif service == 'illiad' and status == 'success':
            self.to = [ patron.email ]
            self.apparent_sender = 'Reply-To: interlibrary_loan@brown.edu'
        elif service == 'illiad' and status == 'login_failed_possibly_blocked':
            self.to = [ patron.email ]
            self.apparent_sender = 'Reply-To: interlibrary_loan@brown.edu'
            self.subject = "Subject: Update on your 'easyBorrow' request -- *problem*"
        else:
            self.to = [ settings.ADMIN_EMAIL ]



        return 'bar'


class Mailer( object ):
    """ Specs email handling. """

    def __init__( self, to_json, reply_to, UNICODE_SUBJECT, UNICODE_MESSAGE, log_identifier ):
        self.UTF8_SMTP_SERVER = settings.MAIL_SMTP_SERVER
        self.UTF8_RAW_TO_JSON = to_json  # json (ensures reliable formatting/encoding), eg: '["addr1@domain.edu", "addr2@domain.com"]'
        self.UTF8_FROM_REAL = settings.MAIL_SENDER  # real 'from' address smtp server will user, eg: 'addr3@domain.edu'
        self.UTF8_FROM_HEADER = settings.MAIL_APPARENT_SENDER  # apparent 'from' string user will see, eg: 'some_system'
        self.UTF8_REPLY_TO_HEADER = reply_to
        self.UNICODE_SUBJECT = UNICODE_SUBJECT
        self.UNICODE_MESSAGE = UNICODE_MESSAGE
        self.log_identifier = log_identifier
        log.debug( '%s - Mailer instantiated' % self.log_identifier )

    def send_email( self ):
        """ Sends email. """
        try:
            TO = self._build_mail_to()  # list of utf-8 entries
            MESSAGE = self.UNICODE_MESSAGE.encode( 'utf-8', 'replace' )  # utf-8
            payload = self._assemble_payload( TO, MESSAGE )
            s = smtplib.SMTP( self.UTF8_SMTP_SERVER )
            s.sendmail( self.UTF8_FROM_REAL, TO, payload.as_string() )
            s.quit()
            log.debug( 'mail sent' )
            return True
        except Exception as e:
            log.error( 'problem sending mail, exception, `%s`' % unicode(repr(e)) )
            return False

    def _build_mail_to( self ):
        """ Builds and returns 'to' list of email addresses.
            Called by send_email() """
        to_emails = json.loads( self.UTF8_RAW_TO_JSON )
        utf8_to_list = []
        for address in to_emails:
            utf8_to_list.append( address.encode('utf-8') )
        return utf8_to_list

    def _assemble_payload( self, TO, MESSAGE ):
        """ Puts together and returns email payload.
            Called by send_email(). """
        payload = MIMEText( MESSAGE )
        payload['To'] = ', '.join( TO )
        payload['From'] = self.UTF8_FROM_HEADER
        payload['Subject'] = Header( self.UNICODE_SUBJECT, 'utf-8' )  # SUBJECT must be unicode
        payload['Reply-to'] = self.UTF8_REPLY_TO_HEADER
        return payload

    # end class Mailer
