# -*- coding: utf-8 -*-

import datetime, imp, json, os, pprint, sys, time
import requests
from types import InstanceType, ModuleType, NoneType


class BD_ApiRunner( object ):
    """ Handles bdpyweb calls. """

    def __init__( self, logger, log_identifier ):
        """ Loads env vars.
            Called by EzBorrowController.py """
        self.logger = logger
        self.log_identifier = log_identifier
        self.bdpyweb_defaults = {
            u'url': unicode( os.environ[u'ezbCTL__BDPYWEB_URL'] ),
            u'api_authorization_code': unicode( os.environ[u'ezbCTL__BDPYWEB_AUTHORIZATION_CODE'] ),
            u'api_identity': unicode( os.environ[u'ezbCTL__BDPYWEB_IDENTITY'] )
            }
        self.api_result = None  # will be dct
        self.api_confirmation_code = None  # will be str
        self.api_found = None  # will be boolean
        self.api_requestable = None  # will be boolean
        self.HISTORY_SQL_PATTERN = unicode( os.environ[u'ezbCTL__INSERT_HISTORY_FULLACTION_SQL_PATTERN'] )

    def setup_api_hit( self, item_instance, web_logger ):
        """ Sets the currently-active-service and updates weblog.
            Called by controller.run_code() """
        item_instance.currentlyActiveService = u'borrowDirect'
        web_logger.post_message( message=u'- in controller; checking BorrowDirect...', identifier=self.log_identifier, importance='info' )
        self.logger.debug( u'- identifier, %s; setup_api_hit() complete' % self.log_identifier )
        return item_instance

    def prepare_params( self, itemInstance ):
        """ Updates item-instance attributes.
            Called by controller.run_code()
            TODO: remove legacy code. """
        if type(itemInstance.patronBarcode) == str:
            itemInstance.patronBarcode = itemInstance.patronBarcode.decode( u'utf-8', u'replace' )
        if type(itemInstance.itemIsbn) == str:
            itemInstance.itemIsbn = itemInstance.itemIsbn.decode( u'utf-8', u'replace' )
        if type(itemInstance.sfxurl) == str:
            itemInstance.sfxurl = itemInstance.sfxurl.decode( u'utf-8', u'replace' )
        bd_data = { u'isbn': itemInstance.itemIsbn, u'user_barcode': itemInstance.patronBarcode }
        return bd_data

    def hit_bd_api( self, isbn, user_barcode ):
        """ Handles bdpyweb call.
            Called by Controller.run_code() """
        self.logger.info( u'%s- starting try_request()' % self.log_identifier )
        parameter_dict = self.prepare_bd_api( isbn, user_barcode )
        try:
            r = requests.post( self.bdpyweb_defaults[u'url'], data=parameter_dict, timeout=300, verify=False )
            self.logger.debug( u'%s- bdpyweb response content, `%s`' % (self.log_identifier, r.content.decode(u'utf-8')) )
            self.api_result = json.loads( r.content )
        except Exception, e:
            self.logger.debug( u'%s- exception on bdpyweb post, `%s`' % (self.log_identifier, pprint.pformat(unicode(repr(e)))) )
        return

    def prepare_bd_api( self, isbn, user_barcode ):
        """ Prepares bd-api dct for post.
            Called by: hit_bd_api() """
        parameter_dict = {
            u'api_authorization_code': self.bdpyweb_defaults[u'api_authorization_code'],
            u'api_identity': self.bdpyweb_defaults[u'api_identity'],
            u'isbn': isbn,
            u'user_barcode': user_barcode }
        self.logger.debug( u'%s- post parameter_dict, `%s`' % (self.log_identifier, parameter_dict) )
        return parameter_dict

    def process_response( self ):
        """ Examines response dict & populates class attributes.
            Called by controller.run_code() """
        if self.api_result and ( type(self.api_result) == dict ) and ( u'requestable' in self.api_result.keys() ):
            if self.api_result[u'requestable'] == True:
                self.api_confirmation_code = self.api_result[u'bd_confirmation_code']
                self.api_found = True
                self.api_requestable = True
        self.logger.debug( u'%s- process_response complete; code, `%s`; found, `%s`; requestable, `%s`' % (self.log_identifier, self.api_confirmation_code, self.api_found, self.api_requestable) )
        return

    def update_history_table( self, utility_code_instance ):
        """ Populates history table based on request result.
            Called by controller.run_code()
            TODO: Call a db class. """
        ( api_confirmation_code, history_table_message ) = self.prep_code_message()
        utf8_sql = self.prep_history_sql( api_confirmation_code, history_table_message )
        utility_code_instance.connectExecute( utf8_sql )
        utility_code_instance.updateLog( message=u'- in tunneler_runners.BD_ApiRunner.update_history_table(); history table updated for ezb#: %s' % self.log_identifier, message_importance=u'low', identifier=self.log_identifier )
        self.logger.debug( u'%s- update_history_table complete' )
        return

    def prep_code_message( self ):
        """ Sets api_confirmation_code and history_table_message vars.
            Called by update_history_table() """
        if self.api_requestable == True:
            api_confirmation_code = self.api_confirmation_code
            history_table_message = u'Request_Successful'
        else:
            api_confirmation_code = u''
            history_table_message = u'not_requestable'
        self.logger.debug( u'%s- prep_code_message complete; local api_confirmation_code, `%s`; history_table_message, `%s`' % (self.log_identifier, api_confirmation_code, history_table_message) )
        return ( api_confirmation_code, history_table_message )

    def prep_history_sql( self, api_confirmation_code, history_table_message ):
        """ Prepares history table update sql.
            Called by update_history_table()
            TODO: when db class exists, remove utf8 encoding. """
        sql = self.HISTORY_SQL_PATTERN % (
          self.log_identifier,
          u'borrowdirect',
          u'attempt',
          history_table_message,
          api_confirmation_code
          )
        utf8_sql = sql.encode( u'utf-8' )  # old code expects utf-8 string
        self.logger.debug( u'%s- prep_history_sql complete; utf8_sql, `%s`' % (self.log_identifier, sql.decode(u'utf-8')) )
        return utf8_sql

    def handle_success( self, itemInstance ):
        """ Updates item-instance attributes on success.
            Called by controller.run_code()
            TODO: remove legacy code. """
        itemInstance.requestSuccessStatus = u'success'
        itemInstance.genericAssignedUserEmail = itemInstance.patronEmail
        itemInstance.genericAssignedReferenceNumber = self.api_confirmation_code
        return itemInstance

    def compare_responses( self, old_runner_instance ):
        """ Writes comparison of old-production and new-api runners.
            Called by Controller.run_code() """
        try:
            comparison_dct = {
              u'old_api_found': old_runner_instance.api_found,
              u'old_api_requestable': old_runner_instance.api_requestable,
              u'new_api_found': self.api_result[u'found'],
              u'new_api_requestable': self.api_result[u'requestable']
              }
            self.logger.debug( u'%s- bd-runner comparison, `%s`' % (self.log_identifier, pprint.pformat(comparison_dct)) )
        except Exception as e:  # handles case where bdpyweb response fails
            self.logger.debug( u'%s- exception on bdpyweb compare write, `%s`' % (self.log_identifier, pprint.pformat(unicode(repr(e)))) )
        return

    # end class BD_ApiRunner



class BD_Runner(object):


  def __init__( self, settings=None  ):
    '''
    - Allows a settings module to be passed in,
        or a settings path to be passed in,
        or a dictionary to be passed in,
        or nothing to be passed in.
    - Sets other attributes.
    - Attributes in caps are passed in; others are calculated.
    '''
    ## discern settings type
    types = [ NoneType, dict, ModuleType, unicode ]
    assert type(settings) in types, Exception( u'Passing in settings is optional, but if used, must be either a dict, a unicode path to a settings module, or a module named settings; current type is: %s' % repr(type(settings)) )
    if isinstance(settings, dict):
      s = imp.new_module( u'settings' )
      for k, v in settings.items():
        setattr( s, k, v )
      settings = s
    elif isinstance(settings, ModuleType):
      pass
    elif isinstance(settings, unicode):  # path
      settings = imp.load_source( u'*', settings )
    ## attribs
    self.EB_REQUEST_NUM = settings.EB_REQUEST_NUM; assert type(self.EB_REQUEST_NUM) == unicode, Exception( u'EB_REQUEST_NUM must be unicode' )
    self.API_URL = settings.API_URL; assert type(self.API_URL) == unicode, Exception( u'API_URL must be unicode' )
    self.API_AUTH_CODE = settings.API_AUTH_CODE; assert type(self.API_AUTH_CODE) == unicode, Exception( u'API_AUTH_CODE must be unicode' )
    self.API_IDENTITY = settings.API_IDENTITY; assert type(self.API_IDENTITY) == unicode, Exception( u'API_IDENTITY must be unicode' )
    self.UNIVERSITY = settings.UNIVERSITY; assert type(self.UNIVERSITY) == unicode, Exception( u'UNIVERSITY must be unicode' )
    self.USER_BARCODE = settings.USER_BARCODE; assert type(self.USER_BARCODE) == unicode, Exception( u'USER_BARCODE must be unicode' )
    self.ISBN = settings.ISBN; assert type(self.ISBN) == unicode, Exception( u'ISBN must be unicode' )  # u'' or u'the-isbn'
    self.WC_URL = settings.WC_URL; assert type(self.WC_URL) == unicode, Exception( u'WC_URL must be unicode' )
    self.OPENURL_PARSER_URL = settings.OPENURL_PARSER_URL; assert type(self.OPENURL_PARSER_URL) == unicode, Exception( u'OPENURL_PARSER_URL must be unicode' )
    self.UC_INSTANCE = settings.UC_INSTANCE; assert type(self.UC_INSTANCE) == InstanceType, Exception( u'UC_INSTANCE must be of InstanceType' )  # for logging
    self.search_type = None
    self.prepared_data_dict = None
    self.worldcat_url_parsed_response = None
    self.string_good_to_go = None
    self.string_title = None
    self.string_author = None
    self.string_date = None
    self.history_table_updated = None
    self.history_table_message = None  # 'no_valid_string' or self.api_result
    self.api_response = None
    self.api_result = None  # api_response 'search_result': 'SUCCESS' or 'FAILURE' (failure meaning not-found or not-requestable)
    self.api_confirmation_code = None  # api_response 'bd_confirmation_code'
    self.api_found = None
    self.api_requestable = None


  def determineSearchType( self ):
    '''
    Determines 'isbn' or 'string' search_type
    '''
    if len( self.ISBN ) > 0:
      self.search_type = u'isbn'
    else:
      self.search_type = u'string'
    self.UC_INSTANCE.updateLog( message=u'- in controller.BD_Runner.determineSearchType(); search_type is: %s' % self.search_type, message_importance=u'low', identifier=self.EB_REQUEST_NUM )
    return


  def prepRequestData( self ):
    '''
    Prepares data dict
    '''
    assert type(self.search_type) == unicode, Exception( u'search_type must be unicode' )
    assert self.search_type in [ u'isbn', u'string' ], Exception( u'search_type must be "isbn" or "string"' )
    data_dict = {
      u'api_authorization_code': self.API_AUTH_CODE,
      u'api_identity': self.API_IDENTITY,
      u'university': self.UNIVERSITY,
      u'user_barcode': self.USER_BARCODE,
      u'command': u'request',
      }
    if self.search_type == u'isbn':
      data_dict[u'isbn'] = self.ISBN
      self.prepared_data_dict = data_dict
    else:
      ## get string
      self.makeSearchString()
      if self.string_good_to_go == True:
        assert type(self.string_title) == unicode, Exception( u'string_title must be unicode' )
        assert type(self.string_author) == unicode, Exception( u'string_author must be unicode' )
        assert type(self.string_date) == unicode, Exception( u'string_date must be unicode' )
        data_dict[u'title'] = self.string_title
        data_dict[u'author'] = self.string_author
        data_dict[u'date'] = self.string_date
        self.prepared_data_dict = data_dict
      else:
        self.prepared_data_dict = u'skip_to_illiad'
    self.UC_INSTANCE.updateLog( message=u'- in controller.BD_Runner.prepRequestData(); self.prepared_data_dict: %s' % self.prepared_data_dict, message_importance=u'low', identifier=self.EB_REQUEST_NUM )
    return


  def makeSearchString( self ):
    '''
    Prepares search string from worldcat url.
    Called by self.prepRequestData()
    '''
    import requests
    self.UC_INSTANCE.updateLog( message=u'- in controller.BD_Runner.makeSearchString(); wc-url to parse: %s' % self.WC_URL, message_importance=u'low', identifier=self.EB_REQUEST_NUM )
    url = self.OPENURL_PARSER_URL
    payload = { u'db_wc_url': self.WC_URL }
    r = requests.get( url, params=payload, verify=False )
    assert type(r.url) == unicode, Exception( u'type(r.url) should be unicode; it is: %s' % type(r.url) )
    self.worldcat_url_parsed_response = r.content.decode(u'utf-8', u'replace')
    try:
      d = json.loads( self.worldcat_url_parsed_response )
      assert sorted(d.keys()) == [u'doc_url', u'request', u'response'], Exception( u'makeSearchString() dict-keys not as expected; they are: %s' % sorted(d.keys()) )
      assert sorted(d[u'request'].keys()) == [u'db_wc_url', u'time'], Exception( u'makeSearchString() request-keys not as expected; they are: %s' % sorted(d[u'request'].keys()) )  # 'db_wc_url' means 'the worldcat url in the database'
      assert sorted(d[u'response'].keys()) == [u'bd_author', u'bd_date', u'bd_title', u'time_taken'], Exception( u'makeSearchString() response-keys not as expected; they are: %s' % sorted(d[u'response'].keys()) )
      self.string_good_to_go = True
      self.string_title = d[u'response'][u'bd_title']
      self.string_author = d[u'response'][u'bd_author']
      self.string_date = d[u'response'][u'bd_date']
    except Exception, e:
      self.string_good_to_go = False
      self.UC_INSTANCE.updateLog( message=u'- in controller.BD_Runner.makeSearchString(); exception handling make-string response is: %s' % repr(e).decode(u'utf-8', u'replace'), message_importance=u'low', identifier=self.EB_REQUEST_NUM )
    self.UC_INSTANCE.updateLog( message=u'- in controller.BD_Runner.makeSearchString(); self.string_good_to_go is: %s' % self.string_good_to_go, message_importance=u'low', identifier=self.EB_REQUEST_NUM )
    self.UC_INSTANCE.updateLog( message=u'- in controller.BD_Runner.makeSearchString(); self.worldcat_url_parsed_response is: %s' % self.worldcat_url_parsed_response, message_importance=u'low', identifier=self.EB_REQUEST_NUM )
    return


  def updateHistoryTable( self ):
    '''
    Updates history table with action-result & ezb request#.
    '''
    try:
      self.history_table_updated == u'init'
      assert type( int(self.EB_REQUEST_NUM) ) == int  # will cause exception if not an int instead of evaluating to False
      ## conditon: no request made due to string-creation failure
      if self.prepared_data_dict == u'skip_to_illiad':
        self.history_table_message = u'no_valid_string'
        self.api_confirmation_code = u''  # instead of None, so the sql statement will work
      ## condition: request was made, so store result
      elif type(self.prepared_data_dict) == dict:
        if self.api_result == u'SUCCESS':
          self.history_table_message = u'Request_Successful'
        elif self.api_result == None:  # some error -- I've seen timeout or main bd website returning 500
          self.history_table_message = u'Error'
          self.api_confirmation_code = u''
        else:  # self.api == u'FAILURE'
          if self.api_found == True and self.api_requestable == False:
            self.history_table_message = u'not_requestable'
          else:  # self.api_found == False:
            self.history_table_message = u'not_found'
      self.UC_INSTANCE.updateLog( message=u'- in controller.BD_Runner.updateHistoryTable(); history_table_message: %s' % self.history_table_message, message_importance=u'low', identifier=self.EB_REQUEST_NUM )

      ## execute sql
      SQL_PATTERN = unicode( os.environ[u'ezbCTL__INSERT_HISTORY_FULLACTION_SQL_PATTERN'] )
      sql = SQL_PATTERN % (
        self.EB_REQUEST_NUM.encode('utf-8', 'replace'),
        'borrowdirect',
        'attempt',
        self.history_table_message.encode(u'utf-8', u'replace'),
        self.api_confirmation_code.encode(u'utf-8', u'replace')
        )  # old code was expecting non-unicode string, so I'll give it.

      self.UC_INSTANCE.connectExecute( sql )  # no useful result currently returned; TODO: try gabbing history record-id
      self.history_table_updated = True
      self.UC_INSTANCE.updateLog( message=u'- in controller.BD_Runner.updateHistoryTable(); history table updated for ezb#: %s' % self.EB_REQUEST_NUM, message_importance=u'low', identifier=self.EB_REQUEST_NUM )
      return
    except Exception, e:
      self.UC_INSTANCE.updateLog( message=u'- in controller.BD_Runner.updateHistoryTable(); exception; repr(e): %s' % repr(e).decode(u'utf-8', u'replace'), message_importance=u'low', identifier=self.EB_REQUEST_NUM )
      return


  def requestItem( self ):
    '''
    Hits the bd_tunneler webservice.
    See tests for response keys.
    Must fail gracefully so-as to pass request on to next service.
    '''
    assert type( self.prepared_data_dict ) == dict, Exception( u'type(prepared_data_dict) should be dict; it is: %s' % type(self.prepared_data_dict) )
    r = requests.post( self.API_URL, data=self.prepared_data_dict, verify=False )
    self.api_response = r.text
    self.UC_INSTANCE.updateLog( message=u'- in controller.BD_Runner.requestItem(); self.api_response: %s' % self.api_response, message_importance=u'low', identifier=self.EB_REQUEST_NUM )
    try:
      d = json.loads( self.api_response )
      self.api_result = d[u'response'][u'search_result']
      self.api_confirmation_code = d[u'response'][u'bd_confirmation_code']
      self.api_found = d[u'response'][u'found']
      self.api_requestable = d[u'response'][u'requestable']
    except Exception, e:
      self.UC_INSTANCE.updateLog( message=u'- in controller.BD_Runner.requestItem(); exception: %s' % repr(e).decode(u'utf-8', u'replace'), message_importance=u'high', identifier=self.EB_REQUEST_NUM )
      ## for history table update
      self.api_result = u'Error'
      self.api_confirmation_code = u''
      self.api_found = u''
      self.api_requestable = u''
    return


  # end class BD_Runner()
