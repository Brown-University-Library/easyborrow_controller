# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pprint
import requests
from easyborrow_controller_code import settings


class WebLogger( object ):
    """ Manages web-logging.
        Because easyborrow has lots of pieces, certain flow steps from different apps and web-apps log to a central db.
        This enables a request to be easily tracked through a web-admin interface. """

    def __init__( self, logger ):
        self.WEBLOG_URL = settings.WEBLOG_URL
        self.WEBLOG_KEY = settings.WEBLOG_KEY
        self.WEBLOG_LEVEL = settings.WEBLOG_LEVEL
        self.logger = logger

    def post_message( self, message, identifier, importance ):
        """ Sends weblog message based on importance. """
        self.logger.debug( 'identifier, `%s`; message, ```%s```; importance, `%s`' % (identifier, pprint.pformat(message), importance) )
        status_code = None
        important_enough = self.evaluate_importance( importance )
        if important_enough:
            status_code = self.run_post( message, identifier )
        return status_code

    def evaluate_importance( self, stated_importance ):
        """ Determines whether to send message based on stated message performance vs env filter setting.
            Returns boolean.
            Called by post_message() """
        assessed_importance = False
        if stated_importance == 'debug' and self.WEBLOG_LEVEL == 'debug':
            assessed_importance = True
        elif stated_importance == 'info' or stated_importance == 'error':
            assessed_importance = True
        return assessed_importance

    def run_post( self, message, identifier ):
        """ Executes post.
            Called by post_message() """
        status_code = None
        params = { 'message': message, 'identifier': identifier, 'key': self.WEBLOG_KEY }
        try:
            r = requests.post( self.WEBLOG_URL, data=params )
            status_code = r.status_code
        except Exception as e:
            self.logger.error( 'failure on weblog post; exception, `%s`' % unicode(repr(e)) )
        return status_code
