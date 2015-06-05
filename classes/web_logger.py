# -*- coding: utf-8 -*-

import os
import requests


class WebLogger( object ):
    """ Manages web-logging.
        Because easyborrow has lots of pieces, certain flow steps from different apps and web-apps log to a central db.
        This enables a request to be easily tracked through a web-admin interface. """

    def __init__( self, logger ):
        self.WEBLOG_URL = unicode( os.environ['ezbCTL__LOG_URL'] )
        self.WEBLOG_KEY = unicode( os.environ['ezbCTL__LOG_KEY'] )
        self.WEBLOGENTRY_MINIMUM_IMPORTANCE_LEVEL = unicode( os.environ['ezbCTL__LOGENTRY_MINIMUM_IMPORTANCE_LEVEL'] )

    def post_message( self, message, identifier, importance,  ):
        """ Sends weblog message based on importance. """
        important_enough = self.evaluate_importance( importance )
        if important_enough:
            self.run_post( message, identifier )
        return

    def evaluate_importance( self, stated_importance ):
        """ Determines whether to send message based on stated message performance vs env filter setting.
            Returns boolean.
            Called by post_message() """
        assessed_importance = False
        if self.WEBLOGENTRY_MINIMUM_IMPORTANCE_LEVEL == u'debug'
            assessed_importance = True
        elif self.WEBLOGENTRY_MINIMUM_IMPORTANCE_LEVEL == u'info' and stated_importance=u'info':
            assessed_importance = True
        return assessed_importance

    def run_post( self, message, identifier ):
        """ Executes post.
            Called by post_message() """
        params = { 'message': message, 'identifier': identifier, 'key': self.WEBLOG_KEY }
        r = requests.post( self.WEBLOG_URL, data=params )
        return
