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
log = logging.getLogger(__name__)


class BD_CallerBib( object ):
    """ Handles bdpy3_web `bib` calls. """

    def __init__( self ):
        """ Loads env vars.
            Called by EzBorrowController.py """
        self.db_handler = None
        self._prep_db_handler()
        self.log_identifier = 'init'
        self.bdpyweb_defaults = {
            'url': settings.BDPYWEB_BIB_URL,  # note: different from other bdpyweb-url setting
            'api_authorization_code': settings.BDPYWEB_AUTHORIZATION_CODE,
            'api_identity': settings.BDPYWEB_IDENTITY
        }
        self.api_result = None  # will be dct
        self.api_confirmation_code = None  # will be str
        self.api_found = None  # will be boolean
        self.api_requestable = None  # will be boolean
        self.HISTORY_SQL_PATTERN = settings.HISTORY_ACTION_SQL
        log.debug( 'BD_CallerBib initialized' )

    def _prep_db_handler( self ):
        """ Initializes db_handler.
            Called by __init__() """
        self.db_handler = Db_Handler( log )
        return

    def prepare_params( self, patron_inst, item_inst ):
        """ Preps parameters for bib call.
            Called by controller.run_code() """
        log.debug( 'about to get `bib_dct`' )
        bib_dct = self.extract_bib( item_inst.knowledgebase_openurl )
        bd_data = {
            'title': item_inst.title,
            # 'author': bib_dct['author'],
            'author': bib_dct['response']['bib']['author'][0]['name'],
            # 'year': bib_dct['year'],
            'year': bib_dct['response']['bib']['year'],
            'user_barcode': patron_inst.barcode }
        log.debug( 'bib bd_data, ```%s```' % pprint.pformat(bd_data) )
        return bd_data

    def extract_bib( self, ourl ):
        """ Parses openurl to return bjson-dct.
            Called by prepare_params() """
        log.debug( 'about to start `param_dct`' )
        log.debug( 'ourl, ```%s```' % ourl )
        param_dct = { 'ourl': ourl }
        try:
            r = requests.get( 'https://library.brown.edu/bib_ourl_api/v1/ourl_to_bib/', params=param_dct )
        except Exception as e:
            msg = unicode(repr(e))
            log.error( 'exception, ```%s```' % msg )
            raise Exception( msg )
        # bib_dct = r.json()
        bib_dct = json.loads( r.content.decode('utf-8') )
        log.debug( 'bib_dct, ```%s```' % pprint.pformat(bib_dct) )
        return bib_dct

    def hit_bd_api( self, title, author, year, user_barcode ):
        """ Executes bdpy3_web bib call.
            Called by Controller.run_code() """
        log.info( '%s- starting try_request()' % self.log_identifier )
        parameter_dict = self.prepare_bd_api_hit( title, author, year, user_barcode )
        try:
            r = requests.post( self.bdpyweb_defaults['url'], data=parameter_dict, timeout=300, verify=False )
            log.debug( '%s- bdpyweb response content, `%s`' % (self.log_identifier, r.content.decode('utf-8')) )
            self.api_result = json.loads( r.content )
        except Exception, e:
            log.debug( '%s- exception on bdpyweb post, `%s`' % (self.log_identifier, pprint.pformat(unicode(repr(e)))) )
        return

    def prepare_bd_api_hit( self, title, author, year, user_barcode ):
        """ Prepares bd-api dct for bib post.
            Called by: hit_bd_api() """
        parameter_dict = {
            'api_authorization_code': self.bdpyweb_defaults['api_authorization_code'],
            'api_identity': self.bdpyweb_defaults['api_identity'],
            'title': title,
            'author': author,
            'year': year,
            'user_barcode': user_barcode }
        log.debug( '%s- parameter_dict to post, ```%s```' % (self.log_identifier, pprint.pformat(parameter_dict)) )
        return parameter_dict

    def process_response( self ):
        """ Examines response & populates instance attributes.
            Called by controller.run_code() """
        if self.api_result == 'test' :
            self.api_confirmation_code = 'the bd transaction number'
            self.api_found = True
            self.api_requestable = True
        log.debug( '%s- process_response complete; code, `%s`; found, `%s`; requestable, `%s`' % (self.log_identifier, self.api_confirmation_code, self.api_found, self.api_requestable) )
        return

    def update_history_table( self ):
        """ Populates history table based on request result.
            Called by controller.run_code() """
        ( api_confirmation_code, history_table_message ) = self.prep_code_message()
        utf8_sql = self.prep_history_sql( api_confirmation_code, history_table_message )
        self.db_handler.run_sql( utf8_sql )
        # self.web_logger.post_message( message='- in tunneler_runners.BD_ApiRunner.update_history_table(); history table updated for ezb#: %s' % self.log_identifier, identifier=self.log_identifier, importance='info' )
        log.debug( 'update_history_table complete' )
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
        log.debug( '%s- prep_code_message complete; local api_confirmation_code, `%s`; history_table_message, `%s`' % (self.log_identifier, api_confirmation_code, history_table_message) )
        return ( api_confirmation_code, history_table_message )

    def prep_history_sql( self, api_confirmation_code, history_table_message ):
        """ Prepares history table update sql.
            Called by update_history_table()
            TODO: when db class exists, remove utf8 encoding. """
        sql = self.HISTORY_SQL_PATTERN % (
            self.log_identifier,
            'borrowdirect',
            'attempt_bd-bib',
            history_table_message,
            api_confirmation_code
        )
        utf8_sql = sql.encode( 'utf-8' )  # old code expects utf-8 string
        log.debug( '%s- prep_history_sql complete; utf8_sql, `%s`' % (self.log_identifier, sql.decode('utf-8')) )
        return utf8_sql

    def handle_success( self, request_inst ):
        """ Updates request_inst attributes on success.
            Called by controller.run_code() """
        request_inst.current_status = 'success'
        request_inst.confirmation_code = self.api_confirmation_code
        return request_inst

    ## end class BD_CallerBib()


class BD_CallerExact( object ):
    """ Handles bdpy3_web `exact` calls. """

    def __init__( self ):
        """ Loads env vars.
            Called by EzBorrowController.py """
        # self.logger = logger
        self.db_handler = None
        self._prep_db_handler()
        self.log_identifier = 'init'
        self.bdpyweb_defaults = {
            'url': settings.BDPYWEB_URL,  # note: different from other bdpyweb-url setting
            'api_authorization_code': settings.BDPYWEB_AUTHORIZATION_CODE,
            'api_identity': settings.BDPYWEB_IDENTITY
        }
        self.api_result = None  # will be dct
        self.api_confirmation_code = None  # will be str
        self.api_found = None  # will be boolean
        self.api_requestable = None  # will be boolean
        self.HISTORY_SQL_PATTERN = settings.HISTORY_ACTION_SQL
        log.debug( 'BD_CallerExact initialized' )

    def _prep_db_handler( self ):
        """ Initializes db_handler.
            Called by __init__() """
        self.db_handler = Db_Handler( log )
        return

    def setup_api_hit( self, item_inst ):
        """ Sets the currently-active-service and updates weblog.
            Called by controller.run_code() """
        item_inst.current_service = 'borrowDirect'
        # web_logger.post_message( message='- in controller; checking BorrowDirect...', identifier=self.log_identifier, importance='info' )
        log.debug( '- identifier, %s; setup_api_hit() complete' % self.log_identifier )
        return item_inst

    def prepare_params( self, patron_inst, item_inst ):
        """ Preps parameters for isbn call.
            Called by controller.run_code() """
        bd_data = { 'isbn': item_inst.isbn, 'user_barcode': patron_inst.barcode }
        return bd_data

    def hit_bd_api( self, isbn, user_barcode ):
        """ Executes bdpy3_web exact call.
            Called by Controller.run_code() """
        log.info( '%s- starting try_request()' % self.log_identifier )
        parameter_dict = self.prepare_bd_api_hit( isbn, user_barcode )
        try:
            r = requests.post( self.bdpyweb_defaults['url'], data=parameter_dict, timeout=300, verify=False )
            log.debug( '%s- bdpyweb response content, `%s`' % (self.log_identifier, r.content.decode('utf-8')) )
            self.api_result = json.loads( r.content )
        except Exception, e:
            log.debug( '%s- exception on bdpyweb post, `%s`' % (self.log_identifier, pprint.pformat(unicode(repr(e)))) )
        return

    def prepare_bd_api_hit( self, isbn, user_barcode ):
        """ Prepares bd-api dct for isbn post.
            Called by: hit_bd_api() """
        parameter_dict = {
            'api_authorization_code': self.bdpyweb_defaults['api_authorization_code'],
            'api_identity': self.bdpyweb_defaults['api_identity'],
            'isbn': isbn,
            'user_barcode': user_barcode }
        log.debug( '%s- post parameter_dict, `%s`' % (self.log_identifier, parameter_dict) )
        return parameter_dict

    def process_response( self ):
        """ Examines response dict & populates class attributes.
            Called by controller.run_code() """
        if self.api_result and ( type(self.api_result) == dict ) and ( 'requestable' in self.api_result.keys() ):
            if self.api_result['requestable'] is True:
                self.api_confirmation_code = self.api_result['bd_confirmation_code']
                self.api_found = True
                self.api_requestable = True
        log.debug( '%s- process_response complete; code, `%s`; found, `%s`; requestable, `%s`' % (self.log_identifier, self.api_confirmation_code, self.api_found, self.api_requestable) )
        return

    def update_history_table( self ):
        """ Populates history table based on request result.
            Called by controller.run_code() """
        ( api_confirmation_code, history_table_message ) = self.prep_code_message()
        utf8_sql = self.prep_history_sql( api_confirmation_code, history_table_message )
        self.db_handler.run_sql( utf8_sql )
        # self.web_logger.post_message( message='- in tunneler_runners.BD_ApiRunner.update_history_table(); history table updated for ezb#: %s' % self.log_identifier, identifier=self.log_identifier, importance='info' )
        log.debug( 'update_history_table complete' )
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
        log.debug( '%s- prep_code_message complete; local api_confirmation_code, `%s`; history_table_message, `%s`' % (self.log_identifier, api_confirmation_code, history_table_message) )
        return ( api_confirmation_code, history_table_message )

    def prep_history_sql( self, api_confirmation_code, history_table_message ):
        """ Prepares history table update sql.
            Called by update_history_table()
            TODO: when db class exists, remove utf8 encoding. """
        sql = self.HISTORY_SQL_PATTERN % (
            self.log_identifier,
            'borrowdirect',
            'attempt_bd-isbn',
            history_table_message,
            api_confirmation_code
        )
        utf8_sql = sql.encode( 'utf-8' )  # old code expects utf-8 string
        log.debug( '%s- prep_history_sql complete; utf8_sql, `%s`' % (self.log_identifier, sql.decode('utf-8')) )
        return utf8_sql

    def handle_success( self, request_inst ):
        """ Updates request_inst attributes on success.
            Called by controller.run_code() """
        request_inst.current_status = 'success'
        request_inst.confirmation_code = self.api_confirmation_code
        return request_inst

    # end class BD_CallerExact()
