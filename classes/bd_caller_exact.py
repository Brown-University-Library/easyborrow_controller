# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json, logging, pprint, urllib, urlparse
import requests
from easyborrow_controller_code import settings
from easyborrow_controller_code.classes.db_handler import Db_Handler


## logger setup
LOG_PATH = settings.LOG_PATH
LOG_LEVEL = settings.LOG_LEVEL
level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
logger = logging.getLogger(__name__)


class BD_CallerExact( object ):
    """ Handles bdpy3_web `exact` calls. """

    def __init__( self, logger, log_identifier ):
        """ Loads env vars.
            Called by EzBorrowController.py """
        self.logger = logger
        self.db_handler = None
        self._prep_db_handler()
        self.log_identifier = log_identifier
        self.bdpyweb_defaults = {
            'url': settings.BDPYWEB_URL,
            'api_authorization_code': settings.BDPYWEB_AUTHORIZATION_CODE,
            'api_identity': settings.BDPYWEB_IDENTITY
        }
        self.api_result = None  # will be dct
        self.api_confirmation_code = None  # will be str
        self.api_found = None  # will be boolean
        self.api_requestable = None  # will be boolean
        self.HISTORY_SQL_PATTERN = settings.HISTORY_ACTION_SQL

    def _prep_db_handler( self ):
        """ Initializes db_handler.
            Called by __init__() """
        self.db_handler = Db_Handler( self.logger )
        return

    def setup_api_hit( self, item_inst, web_logger ):
        """ Sets the currently-active-service and updates weblog.
            Called by controller.run_code() """
        item_inst.current_service = 'borrowDirect'
        web_logger.post_message( message='- in controller; checking BorrowDirect...', identifier=self.log_identifier, importance='info' )
        self.logger.debug( '- identifier, %s; setup_api_hit() complete' % self.log_identifier )
        return item_inst

    def prepare_params( self, patron_inst, item_inst ):
        """ Preps bd-api parameters.
            Called by controller.run_code() """
        bd_data = { 'isbn': item_inst.isbn, 'user_barcode': patron_inst.barcode }
        return bd_data

    def hit_bd_api( self, isbn, user_barcode ):
        """ Handles bdpyweb call.
            Called by Controller.run_code() """
        self.logger.info( '%s- starting try_request()' % self.log_identifier )
        parameter_dict = self.prepare_bd_api( isbn, user_barcode )
        try:
            r = requests.post( self.bdpyweb_defaults['url'], data=parameter_dict, timeout=300, verify=False )
            self.logger.debug( '%s- bdpyweb response content, `%s`' % (self.log_identifier, r.content.decode('utf-8')) )
            self.api_result = json.loads( r.content )
        except Exception, e:
            self.logger.debug( '%s- exception on bdpyweb post, `%s`' % (self.log_identifier, pprint.pformat(unicode(repr(e)))) )
        return

    def prepare_bd_api( self, isbn, user_barcode ):
        """ Prepares bd-api dct for post.
            Called by: hit_bd_api() """
        parameter_dict = {
            'api_authorization_code': self.bdpyweb_defaults['api_authorization_code'],
            'api_identity': self.bdpyweb_defaults['api_identity'],
            'isbn': isbn,
            'user_barcode': user_barcode }
        self.logger.debug( '%s- post parameter_dict, `%s`' % (self.log_identifier, parameter_dict) )
        return parameter_dict

    def process_response( self ):
        """ Examines response dict & populates class attributes.
            Called by controller.run_code() """
        if self.api_result and ( type(self.api_result) == dict ) and ( 'requestable' in self.api_result.keys() ):
            if self.api_result['requestable'] is True:
                self.api_confirmation_code = self.api_result['bd_confirmation_code']
                self.api_found = True
                self.api_requestable = True
        self.logger.debug( '%s- process_response complete; code, `%s`; found, `%s`; requestable, `%s`' % (self.log_identifier, self.api_confirmation_code, self.api_found, self.api_requestable) )
        return

    def update_history_table( self ):
        """ Populates history table based on request result.
            Called by controller.run_code() """
        ( api_confirmation_code, history_table_message ) = self.prep_code_message()
        utf8_sql = self.prep_history_sql( api_confirmation_code, history_table_message )
        self.db_handler.run_sql( utf8_sql )
        self.web_logger.post_message( message='- in tunneler_runners.BD_ApiRunner.update_history_table(); history table updated for ezb#: %s' % self.log_identifier, identifier=self.log_identifier, importance='info' )
        self.logger.debug( 'update_history_table complete' )
        return

    def prep_code_message( self ):
        """ Sets api_confirmation_code and history_table_message vars.
            Called by update_history_table() """
        if self.api_requestable is True:
            api_confirmation_code = self.api_confirmation_code
            history_table_message = 'Request_Successful'
        else:
            api_confirmation_code = ''
            history_table_message = 'not_requestable'
        self.logger.debug( '%s- prep_code_message complete; local api_confirmation_code, `%s`; history_table_message, `%s`' % (self.log_identifier, api_confirmation_code, history_table_message) )
        return ( api_confirmation_code, history_table_message )

    def prep_history_sql( self, api_confirmation_code, history_table_message ):
        """ Prepares history table update sql.
            Called by update_history_table()
            TODO: when db class exists, remove utf8 encoding. """
        sql = self.HISTORY_SQL_PATTERN % (
            self.log_identifier,
            'borrowdirect',
            'attempt',
            history_table_message,
            api_confirmation_code
        )
        utf8_sql = sql.encode( 'utf-8' )  # old code expects utf-8 string
        self.logger.debug( '%s- prep_history_sql complete; utf8_sql, `%s`' % (self.log_identifier, sql.decode('utf-8')) )
        return utf8_sql

    def handle_success( self, request_inst ):
        """ Updates request_inst attributes on success.
            Called by controller.run_code() """
        request_inst.current_status = 'success'
        request_inst.confirmation_code = self.api_confirmation_code
        return request_inst

    # end class BD_CallerExact()
