# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, imp, json, logging, os, pprint, sys, time
import requests
from easyborrow_controller_code import settings
from easyborrow_controller_code.classes.db_handler import Db_Handler
from easyborrow_controller_code.classes.web_logger import WebLogger
from types import InstanceType, ModuleType, NoneType


## file and web-loggers
LOG_PATH = settings.LOG_PATH
LOG_LEVEL = settings.LOG_LEVEL
level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
logger = logging.getLogger(__name__)
web_logger = WebLogger( logger )


class IlliadApiRunner( object ):
    """ Handles calls to the illiad api. """

    # def __init__( self, request_inst ):
    #     self.log_identifier = request_inst.request_number

    def __init__( self, request_inst ):
        self.log_identifier = request_inst.request_number
        self.HISTORY_SQL_PATTERN = settings.HISTORY_ACTION_SQL
        self.db_handler = Db_Handler( logger )
        self.web_logger = WebLogger( logger )

    def make_parameters( self, request_inst, patron_inst, item_inst ):
        """ Builds parameter_dict for the api hit.
            Note that this tunneler api-hit _used to_ handle new-user registration; that is all now handled at the landing page.
            Called by controller.run_code() """
        parameter_dict = {
            'auth_key': settings.ILLIAD_API_KEY,
            'request_id': self.log_identifier,
            'first_name': patron_inst.firstname,  # was used for new_user registration
            'last_name': patron_inst.lastname,  # wasused for new_user registration
            'username': patron_inst.eppn,  # was for login _and_ new_user registration
            'address': '',  # was used for new_user registration
            'email': patron_inst.email,  # was used for new_user registration
            'oclc_number': item_inst.oclc_num,
            'openurl': self._make_openurl_segment( item_inst.knowledgebase_openurl ),
            'patron_barcode': patron_inst.barcode,
            'patron_department': '',  # was used for new_user registration
            'patron_status': '',  # was used for new_user registration
            'phone': '',  # was used for new_user registration
            'volumes': '',  # perceived but not handled by dj_ill_submission -- 2016-01-17 TODO, I think this should be added to the `notes`
            }
        return_dct = { 'parameter_dict': parameter_dict }
        logger.debug( 'return_dct, ```%s```' % pprint.pformat(return_dct) )
        return return_dct

    def _make_openurl_segment( self, initial_url ):
        """ Prepares the openurl segment.
            Called by make_parameters() """
        try:
            logger.debug( 'id, `%s`; initial_url is: %s' % (self.log_identifier, initial_url) )
            openurl = initial_url[ initial_url.find( 'serialssolutions.com/?' ) + 22 : ]  # TODO: change this to use the urlparse library
            openurl = openurl.replace( 'genre=unknown', 'genre=book' )
            logger.debug( 'id, `%s`; openurl is: %s' % (self.log_identifier, openurl) )
            return openurl
        except Exception as e:
            message = '- in tunneler_runners.IlliadApiRunner._make_openurl_segment(); exception, `%s`' % unicode( repr(e) )
            web_logger.post_message( message=message, identifier=log_identifier, importance='error' )
            raise Exception( message )
            return

    def submit_request( self, parameter_dict ):
        """ Submits the illiad request.
            Called by controller.run_code() """
        try:
            url = settings.ILLIAD_API_URL
            headers = { 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8' }
            r = requests.post( url, data=parameter_dict, headers=headers, timeout=60, verify=False )
            logger.debug( 'id, `%s`; ws response text, ```%s```' % (self.log_identifier, r.text) )  # TODO, log used encoding and set it explicitly
            return_dict = json.loads( r.text )
            web_logger.post_message( message='- in IlliadApiRunner.submit_request(); return_dict: %s' % pprint.pformat(return_dict), identifier=self.log_identifier, importance='info' )
            return return_dict
        except Exception as e:
            message = '- in IlliadApiRunner.submit_request(); exception: %s' % unicode( repr(e) )
            web_logger.post_message( message=message, identifier=self.log_identifier, importance='error' )
            return { 'error_message': message }

    def evaluate_response( self, request_inst, send_result_dct ):
        """ Updates request_inst and updates history note.
            Called by controller.run_code() """
        if send_result_dict.get('status') == 'submission_successful':
            request_inst.current_status = 'success'
        else:
            request_inst.current_status = send_result_dct.get('status', 'in_process' )
        request_inst.confirmation_code = send_result_dct.get( 'transaction_number', '' )
        self.update_history_table( request_inst )
        return request_inst

    def update_history_table( self, request_inst ):
        """ Populates history table based on request result.
            Called by evaluate_response() """
        ( api_confirmation_code, history_table_message ) = self.prep_code_message()
        sql = self.prep_history_sql( api_confirmation_code, history_table_message )
        self.db_handler.run_sql( sql )
        self.web_logger.post_message( message='- in tunneler_runners.IlliadApiRunner.update_history_table(); history table updated for ezb#: %s' % self.log_identifier, identifier=self.log_identifier, importance='info' )
        logger.debug( 'update_history_table complete' )
        return

    def prep_history_sql( self, request_inst ):
        """ Prepares history table update sql.
            Called by update_history_table() """
        sql = self.HISTORY_SQL_PATTERN % (
          request_inst.request_number,
          'illiad',
          'attempt',
          request_inst.current_status,
          request_inst.confirmation_code
          )
        logger.debug( '%s- history_sql, `%s`' % (self.log_identifier, sql) )
        return sql

    # end class IlliadApiRunner


class BD_ApiRunner( object ):
    """ Handles bdpyweb calls. """

    def __init__( self, logger, log_identifier ):
        """ Loads env vars.
            Called by EzBorrowController.py """
        self.logger = logger
        self.web_logger = None
        self._prep_web_logger()
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

    def _prep_web_logger( self ):
        """ Initializes web_logger.
            Called by __init__() """
        self.web_logger = WebLogger( self.logger )
        return

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

    def prepare_params( self,  patron_inst, item_inst ):
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
            if self.api_result['requestable'] == True:
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
        if self.api_requestable == True:
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

    def compare_responses( self, old_runner_instance ):
        """ Writes comparison of old-production and new-api runners.
            Called by Controller.run_code() """
        try:
            comparison_dct = {
              'old_api_found': old_runner_instance.api_found,
              'old_api_requestable': old_runner_instance.api_requestable,
              'new_api_found': self.api_result['found'],
              'new_api_requestable': self.api_result['requestable']
              }
            self.logger.debug( '%s- bd-runner comparison, `%s`' % (self.log_identifier, pprint.pformat(comparison_dct)) )
        except Exception as e:  # handles case where bdpyweb response fails
            self.logger.debug( '%s- exception on bdpyweb compare write, `%s`' % (self.log_identifier, pprint.pformat(unicode(repr(e)))) )
        return

    # end class BD_ApiRunner
