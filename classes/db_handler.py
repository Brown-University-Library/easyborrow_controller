# -*- coding: utf-8 -*-

import os, datetime, pprint
import MySQLdb


class Db_Handler(object):
    """ Manages db calls. """

    def __init__(self, logger ):
        """ Sets up basics. """
        self.DB_HOST = unicode( os.environ[u'ezbCTL__DB_HOST'] )
        self.DB_PORT = int( os.environ[u'ezbCTL__DB_PORT'] )
        self.DB_USERNAME = unicode( os.environ[u'ezbCTL__DB_USERNAME'] )
        self.DB_PASSWORD = unicode( os.environ[u'ezbCTL__DB_PASSWORD'] )
        self.DB_NAME = unicode( os.environ[u'ezbCTL__DB_NAME'] )
        self.connection_object = None  # populated during queries
        self.cursor_object = None  # populated during queries
        self.logger = logger
        self.logger.debug( u'DB_Handler instantiated' )

    ## main functions ##

    def run_select( self, sql ):
        """ Executes sql, returns key-value dict.
            Called by controller.run_record_search() """
        try:
            dict_list = None
            self._setup_db_connection()
            if self.cursor_object:
                dict_list = self._run_execute( sql )
                dict_list = self._unicodify_resultset( dict_list )
            return dict_list
        except Exception as e:
            self.logger.error( u'error: %s' % unicode(repr(e).decode(u'utf8', u'replace')) )
            return None
        finally:
            self._close_db_connection()

    ## helper functions ##

    def _setup_db_connection( self ):
        """ Sets up connection; populates instance attributes.
            Called by run_select() """
        try:
            self.connection_object = MySQLdb.connect(
                host=self.DB_HOST, port=self.DB_PORT, user=self.DB_USERNAME, passwd=self.DB_PASSWORD, db=self.DB_NAME )
            self.cursor_object = self.connection_object.cursor( MySQLdb.cursors.DictCursor )
            return
        except Exception as e:
            self.logger.error( u'error: %s' % unicode(repr(e).decode(u'utf8', u'replace')) )
            return

    def _run_execute( self, sql ):
        """ Executes select; returns tuple of row-dicts.
            Example return data: ( {row1field1key: row1field1value, row1field2key: row1field2value}, {row2field1key: row2field1value, row2field2key: row2field2value} )
            Called by run_select() """
        self.cursor_object.execute( sql )
        dict_list = self.cursor_object.fetchall()  # really a tuple of row-dicts
        self.logger.debug( u'dict_list unicodified, ```%s```' % pprint.pformat(dict_list) )
        return dict_list

    def _unicodify_resultset( self, dict_list ):
        """ Ensures result-set's keys & values are unicode-strings.
            Called by run_select() """
        try:
            result_list = []
            for row_dict in dict_list:
                new_row_dict = {}
                for key,value in row_dict.items():
                    if type(value) == datetime.datetime:
                        value = unicode(value)
                    new_row_dict[ unicode(key) ] = unicode(value)
                result_list.append( new_row_dict )
            return result_list
        except Exception as e:
            self.logger.error( u'error: %s' % unicode(repr(e).decode(u'utf8', u'replace')) )

    def _close_db_connection( self ):
        """ Closes db connection.
            Called by run_select() """
        try:
            self.cursor_object.close()
            self.connection_object.close()
            self.logger.debug( u'db connection closed' )
            return
        except Exception as e:
            self.logger.error( u'error: %s' % unicode(repr(e).decode(u'utf8', u'replace')) )

  # def execute_sql(self, sql):
  #   """ Executes sql; returns tuple of row-dicts.
  #       Example return data: ( {row1field1key: row1field1value, row1field2key: row1field2value}, {row2field1key: row2field1value, row2field2key: row2field2value} )
  #       Called by Controller.get_new_data(), self.update_request_status() """
  #   try:
  #     self._setup_db_connection()
  #     if not self.cursor_object:
  #       return
  #     self.cursor_object.execute( sql )
  #     dict_list = self.cursor_object.fetchall()  # really a tuple of row-dicts

  #     self.db_logger.update_log( message=u'- in dev_ezb_controller.py; uc.DB_Handler.execute_sql(); dict_list: %s' % dict_list, message_importance='low' )
  #     dict_list = self._unicodify_resultset( dict_list )
  #     self.db_logger.update_log( message=u'- in dev_ezb_controller.py; uc.DB_Handler.execute_sql(); dict_list NOW: %s' % dict_list, message_importance='low' )

  #     return dict_list
  #   except Exception as e:
  #     message = u'- in dev_ezb_controller.py; uc.DB_Handler.execute_sql(); error: %s' % unicode( repr(e).decode(u'utf8', u'replace') )
  #     self.db_logger.update_log( message=message, message_importance='high' )
  #     return None
  #   finally:
  #     self._close_db_connection()

  # def _setup_db_connection( self ):
  #   """ Sets up connection; populates instance attributes.
  #       Called by run_select() """
  #   try:
  #     import MySQLdb
  #     self.connection_object = MySQLdb.connect(
  #       host=self.db_host, port=self.db_port, user=self.db_username, passwd=self.db_password, db=self.db_name )
  #     self.cursor_object = self.connection_object.cursor(MySQLdb.cursors.DictCursor)
  #     return
  #   except Exception as e:
  #     message = u'- in dev_ezb_controller.py; uc.DB_Handler._setup_db_connection(); error: %s' % unicode( repr(e).decode(u'utf8', u'replace') )
  #     self.db_logger.update_log( message=message, message_importance='high' )

  # def _unicodify_resultset( self, dict_list ):
  #   """ Returns dict with keys and values as unicode-strings. """
  #   try:
  #     result_list = []
  #     for row_dict in dict_list:
  #       new_row_dict = {}
  #       for key,value in row_dict.items():
  #         if type(value) == datetime.datetime:
  #           value = unicode(value)
  #         new_row_dict[ unicode(key) ] = unicode(value)
  #       result_list.append( new_row_dict )
  #     return result_list
  #   except Exception as e:
  #     message = u'- in dev_ezb_controller.py; uc.DB_Handler._unicodify_resultset(); error: %s' % unicode( repr(e).decode(u'utf8', u'replace') )
  #     self.db_logger.update_log( message=message, message_importance='high' )

  # def _close_db_connection( self ):
  #   """ Closes db connection.
  #       Called by run_select() """
  #   try:
  #     self.cursor_object.close()
  #     self.connection_object.close()
  #     message = u'- in dev_ezb_controller.py; uc.DB_Handler._close_db_connection(); db connection closed'
  #     self.db_logger.update_log( message=message, message_importance='low' )
  #     return
  #   except Exception as e:
  #     message = u'- in dev_ezb_controller.py; uc.DB_Handler._close_db_connection(); error: %s' % unicode( repr(e).decode(u'utf8', u'replace') )
  #     self.db_logger.update_log( message=message, message_importance='high' )

  # def update_request_status( self, row_id, status ):
  #   """ Updates request table status field.
  #       Called by ezb_controller.py """
  #   SQL_PATTERN = unicode( os.environ[u'ezbCTL__UPDATE_REQUEST_STATUS_SQL_PATTERN'] )
  #   sql = SQL_PATTERN % ( status, row_id )
  #   result = self.execute_sql( sql )
  #   self.db_logger.update_log(
  #     message=u'- in dev_ezb_controller.py; uc.DB_Handler.update_request_status(); status updated to %s' % status, message_importance=u'low' )
  #   return

  # def update_history_note( self, request_id, note ):
  #   """ Updates history table note field.
  #       Called by ezb_controller.py """

  #   SQL_PATTERN = unicode( os.environ[u'ezbCTL__INSERT_HISTORY_NOTE_SQL_PATTERN'] )
  #   sql = SQL_PATTERN % ( request_id, note )

  #   result = self.execute_sql( sql )
  #   self.db_logger.update_log(
  #     message=u'- in dev_ezb_controller.py; uc.DB_Handler.update_history_note(); note updated', message_importance=u'low' )
  #   return

  # end class DB_Handler()
