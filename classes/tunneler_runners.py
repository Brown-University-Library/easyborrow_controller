# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, imp, json, os, pprint, sys, time
import requests
from easyborrow_controller_code import settings
from easyborrow_controller_code.classes.db_handler import Db_Handler
from easyborrow_controller_code.classes.web_logger import WebLogger
from types import InstanceType, ModuleType, NoneType


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

    def setup_api_hit( self, item_instance, web_logger ):
        """ Sets the currently-active-service and updates weblog.
            Called by controller.run_code() """
        item_instance.currentlyActiveService = 'borrowDirect'
        web_logger.post_message( message='- in controller; checking BorrowDirect...', identifier=self.log_identifier, importance='info' )
        self.logger.debug( '- identifier, %s; setup_api_hit() complete' % self.log_identifier )
        return item_instance

    def prepare_params( self, itemInstance ):
        """ Updates item-instance attributes.
            Called by controller.run_code()
            TODO: remove legacy code. """
        if type(itemInstance.patronBarcode) == str:
            itemInstance.patronBarcode = itemInstance.patronBarcode.decode( 'utf-8', 'replace' )
        if type(itemInstance.itemIsbn) == str:
            itemInstance.itemIsbn = itemInstance.itemIsbn.decode( 'utf-8', 'replace' )
        if type(itemInstance.sfxurl) == str:
            itemInstance.sfxurl = itemInstance.sfxurl.decode( 'utf-8', 'replace' )
        bd_data = { 'isbn': itemInstance.itemIsbn, 'user_barcode': itemInstance.patronBarcode }
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

    def update_history_table( self, utility_code_instance ):
        """ Populates history table based on request result.
            Called by controller.run_code()
            TODO: Call a db class. """
        ( api_confirmation_code, history_table_message ) = self.prep_code_message()
        utf8_sql = self.prep_history_sql( api_confirmation_code, history_table_message )
        utility_code_instance.connectExecute( utf8_sql )
        self.web_logger.post_message( message='- in tunneler_runners.BD_ApiRunner.update_history_table(); history table updated for ezb#: %s' % self.log_identifier, identifier=self.log_identifier, importance='info' )
        self.logger.debug( '%s- update_history_table complete' )
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

    def handle_success( self, itemInstance ):
        """ Updates item-instance attributes on success.
            Called by controller.run_code()
            TODO: remove legacy code. """
        itemInstance.requestSuccessStatus = 'success'
        itemInstance.genericAssignedUserEmail = itemInstance.patronEmail
        itemInstance.genericAssignedReferenceNumber = self.api_confirmation_code
        return itemInstance

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
