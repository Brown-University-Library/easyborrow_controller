# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, imp, json, os, pprint, sys, time
import requests
from easyborrow_controller_code import settings
from types import InstanceType, ModuleType, NoneType


class BD_ApiRunner( object ):
    """ Handles bdpyweb calls. """

    def __init__( self, logger, log_identifier ):
        """ Loads env vars.
            Called by EzBorrowController.py """
        self.logger = logger
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
        utility_code_instance.updateLog( message='- in tunneler_runners.BD_ApiRunner.update_history_table(); history table updated for ezb#: %s' % self.log_identifier, message_importance='low', identifier=self.log_identifier )
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



# class BD_Runner(object):


#   def __init__( self, settings=None  ):
#     '''
#     - Allows a settings module to be passed in,
#         or a settings path to be passed in,
#         or a dictionary to be passed in,
#         or nothing to be passed in.
#     - Sets other attributes.
#     - Attributes in caps are passed in; others are calculated.
#     '''
#     ## discern settings type
#     types = [ NoneType, dict, ModuleType, unicode ]
#     assert type(settings) in types, Exception( 'Passing in settings is optional, but if used, must be either a dict, a unicode path to a settings module, or a module named settings; current type is: %s' % repr(type(settings)) )
#     if isinstance(settings, dict):
#       s = imp.new_module( 'settings' )
#       for k, v in settings.items():
#         setattr( s, k, v )
#       settings = s
#     elif isinstance(settings, ModuleType):
#       pass
#     elif isinstance(settings, unicode):  # path
#       settings = imp.load_source( '*', settings )
#     ## attribs
#     self.EB_REQUEST_NUM = settings.EB_REQUEST_NUM; assert type(self.EB_REQUEST_NUM) == unicode, Exception( 'EB_REQUEST_NUM must be unicode' )
#     self.API_URL = settings.API_URL; assert type(self.API_URL) == unicode, Exception( 'API_URL must be unicode' )
#     self.API_AUTH_CODE = settings.API_AUTH_CODE; assert type(self.API_AUTH_CODE) == unicode, Exception( 'API_AUTH_CODE must be unicode' )
#     self.API_IDENTITY = settings.API_IDENTITY; assert type(self.API_IDENTITY) == unicode, Exception( 'API_IDENTITY must be unicode' )
#     self.UNIVERSITY = settings.UNIVERSITY; assert type(self.UNIVERSITY) == unicode, Exception( 'UNIVERSITY must be unicode' )
#     self.USER_BARCODE = settings.USER_BARCODE; assert type(self.USER_BARCODE) == unicode, Exception( 'USER_BARCODE must be unicode' )
#     self.ISBN = settings.ISBN; assert type(self.ISBN) == unicode, Exception( 'ISBN must be unicode' )  # '' or 'the-isbn'
#     self.WC_URL = settings.WC_URL; assert type(self.WC_URL) == unicode, Exception( 'WC_URL must be unicode' )
#     self.OPENURL_PARSER_URL = settings.OPENURL_PARSER_URL; assert type(self.OPENURL_PARSER_URL) == unicode, Exception( 'OPENURL_PARSER_URL must be unicode' )
#     self.UC_INSTANCE = settings.UC_INSTANCE; assert type(self.UC_INSTANCE) == InstanceType, Exception( 'UC_INSTANCE must be of InstanceType' )  # for logging
#     self.HISTORY_SQL_PATTERN = settings.HISTORY_ACTION_SQL
#     self.search_type = None
#     self.prepared_data_dict = None
#     self.worldcat_url_parsed_response = None
#     self.string_good_to_go = None
#     self.string_title = None
#     self.string_author = None
#     self.string_date = None
#     self.history_table_updated = None
#     self.history_table_message = None  # 'no_valid_string' or self.api_result
#     self.api_response = None
#     self.api_result = None  # api_response 'search_result': 'SUCCESS' or 'FAILURE' (failure meaning not-found or not-requestable)
#     self.api_confirmation_code = None  # api_response 'bd_confirmation_code'
#     self.api_found = None
#     self.api_requestable = None


#   def determineSearchType( self ):
#     '''
#     Determines 'isbn' or 'string' search_type
#     '''
#     if len( self.ISBN ) > 0:
#       self.search_type = 'isbn'
#     else:
#       self.search_type = 'string'
#     self.UC_INSTANCE.updateLog( message='- in controller.BD_Runner.determineSearchType(); search_type is: %s' % self.search_type, message_importance='low', identifier=self.EB_REQUEST_NUM )
#     return


#   def prepRequestData( self ):
#     '''
#     Prepares data dict
#     '''
#     assert type(self.search_type) == unicode, Exception( 'search_type must be unicode' )
#     assert self.search_type in [ 'isbn', 'string' ], Exception( 'search_type must be "isbn" or "string"' )
#     data_dict = {
#       'api_authorization_code': self.API_AUTH_CODE,
#       'api_identity': self.API_IDENTITY,
#       'university': self.UNIVERSITY,
#       'user_barcode': self.USER_BARCODE,
#       'command': 'request',
#       }
#     if self.search_type == 'isbn':
#       data_dict['isbn'] = self.ISBN
#       self.prepared_data_dict = data_dict
#     else:
#       ## get string
#       self.makeSearchString()
#       if self.string_good_to_go == True:
#         assert type(self.string_title) == unicode, Exception( 'string_title must be unicode' )
#         assert type(self.string_author) == unicode, Exception( 'string_author must be unicode' )
#         assert type(self.string_date) == unicode, Exception( 'string_date must be unicode' )
#         data_dict['title'] = self.string_title
#         data_dict['author'] = self.string_author
#         data_dict['date'] = self.string_date
#         self.prepared_data_dict = data_dict
#       else:
#         self.prepared_data_dict = 'skip_to_illiad'
#     self.UC_INSTANCE.updateLog( message='- in controller.BD_Runner.prepRequestData(); self.prepared_data_dict: %s' % self.prepared_data_dict, message_importance='low', identifier=self.EB_REQUEST_NUM )
#     return


#   def makeSearchString( self ):
#     '''
#     Prepares search string from worldcat url.
#     Called by self.prepRequestData()
#     '''
#     # import requests
#     self.UC_INSTANCE.updateLog( message='- in controller.BD_Runner.makeSearchString(); wc-url to parse: %s' % self.WC_URL, message_importance='low', identifier=self.EB_REQUEST_NUM )
#     url = self.OPENURL_PARSER_URL
#     payload = { 'db_wc_url': self.WC_URL }
#     r = requests.get( url, params=payload, verify=False )
#     assert type(r.url) == unicode, Exception( 'type(r.url) should be unicode; it is: %s' % type(r.url) )
#     self.worldcat_url_parsed_response = r.content.decode('utf-8', 'replace')
#     try:
#       d = json.loads( self.worldcat_url_parsed_response )
#       assert sorted(d.keys()) == ['doc_url', 'request', 'response'], Exception( 'makeSearchString() dict-keys not as expected; they are: %s' % sorted(d.keys()) )
#       assert sorted(d['request'].keys()) == ['db_wc_url', 'time'], Exception( 'makeSearchString() request-keys not as expected; they are: %s' % sorted(d['request'].keys()) )  # 'db_wc_url' means 'the worldcat url in the database'
#       assert sorted(d['response'].keys()) == ['bd_author', 'bd_date', 'bd_title', 'time_taken'], Exception( 'makeSearchString() response-keys not as expected; they are: %s' % sorted(d['response'].keys()) )
#       self.string_good_to_go = True
#       self.string_title = d['response']['bd_title']
#       self.string_author = d['response']['bd_author']
#       self.string_date = d['response']['bd_date']
#     except Exception, e:
#       self.string_good_to_go = False
#       self.UC_INSTANCE.updateLog( message='- in controller.BD_Runner.makeSearchString(); exception handling make-string response is: %s' % repr(e).decode('utf-8', 'replace'), message_importance='low', identifier=self.EB_REQUEST_NUM )
#     self.UC_INSTANCE.updateLog( message='- in controller.BD_Runner.makeSearchString(); self.string_good_to_go is: %s' % self.string_good_to_go, message_importance='low', identifier=self.EB_REQUEST_NUM )
#     self.UC_INSTANCE.updateLog( message='- in controller.BD_Runner.makeSearchString(); self.worldcat_url_parsed_response is: %s' % self.worldcat_url_parsed_response, message_importance='low', identifier=self.EB_REQUEST_NUM )
#     return


#   def updateHistoryTable( self ):
#     '''
#     Updates history table with action-result & ezb request#.
#     '''
#     try:
#       self.history_table_updated == 'init'
#       assert type( int(self.EB_REQUEST_NUM) ) == int  # will cause exception if not an int instead of evaluating to False
#       ## conditon: no request made due to string-creation failure
#       if self.prepared_data_dict == 'skip_to_illiad':
#         self.history_table_message = 'no_valid_string'
#         self.api_confirmation_code = ''  # instead of None, so the sql statement will work
#       ## condition: request was made, so store result
#       elif type(self.prepared_data_dict) == dict:
#         if self.api_result == 'SUCCESS':
#           self.history_table_message = 'Request_Successful'
#         elif self.api_result == None:  # some error -- I've seen timeout or main bd website returning 500
#           self.history_table_message = 'Error'
#           self.api_confirmation_code = ''
#         else:  # self.api == 'FAILURE'
#           if self.api_found == True and self.api_requestable == False:
#             self.history_table_message = 'not_requestable'
#           else:  # self.api_found == False:
#             self.history_table_message = 'not_found'
#       self.UC_INSTANCE.updateLog( message='- in controller.BD_Runner.updateHistoryTable(); history_table_message: %s' % self.history_table_message, message_importance='low', identifier=self.EB_REQUEST_NUM )

#       sql = self.HISTORY_SQL_PATTERN % (
#         self.EB_REQUEST_NUM.encode('utf-8', 'replace'),
#         'borrowdirect',
#         'attempt',
#         self.history_table_message.encode('utf-8', 'replace'),
#         self.api_confirmation_code.encode('utf-8', 'replace')
#         )  # old code was expecting non-unicode string, so I'll give it.

#       self.UC_INSTANCE.connectExecute( sql )  # no useful result currently returned; TODO: try gabbing history record-id
#       self.history_table_updated = True
#       self.UC_INSTANCE.updateLog( message='- in controller.BD_Runner.updateHistoryTable(); history table updated for ezb#: %s' % self.EB_REQUEST_NUM, message_importance='low', identifier=self.EB_REQUEST_NUM )
#       return
#     except Exception, e:
#       self.UC_INSTANCE.updateLog( message='- in controller.BD_Runner.updateHistoryTable(); exception; repr(e): %s' % repr(e).decode('utf-8', 'replace'), message_importance='low', identifier=self.EB_REQUEST_NUM )
#       return


#   def requestItem( self ):
#     '''
#     Hits the bd_tunneler webservice.
#     See tests for response keys.
#     Must fail gracefully so-as to pass request on to next service.
#     '''
#     assert type( self.prepared_data_dict ) == dict, Exception( 'type(prepared_data_dict) should be dict; it is: %s' % type(self.prepared_data_dict) )
#     r = requests.post( self.API_URL, data=self.prepared_data_dict, verify=False )
#     self.api_response = r.text
#     self.UC_INSTANCE.updateLog( message='- in controller.BD_Runner.requestItem(); self.api_response: %s' % self.api_response, message_importance='low', identifier=self.EB_REQUEST_NUM )
#     try:
#       d = json.loads( self.api_response )
#       self.api_result = d['response']['search_result']
#       self.api_confirmation_code = d['response']['bd_confirmation_code']
#       self.api_found = d['response']['found']
#       self.api_requestable = d['response']['requestable']
#     except Exception, e:
#       self.UC_INSTANCE.updateLog( message='- in controller.BD_Runner.requestItem(); exception: %s' % repr(e).decode('utf-8', 'replace'), message_importance='high', identifier=self.EB_REQUEST_NUM )
#       ## for history table update
#       self.api_result = 'Error'
#       self.api_confirmation_code = ''
#       self.api_found = ''
#       self.api_requestable = ''
#     return


#   # end class BD_Runner()
