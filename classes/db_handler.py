# -*- coding: utf-8 -*-

import os, datetime, pprint
import MySQLdb
from easyborrow_controller_code import settings


class Db_Handler(object):
    """ Manages db calls. """

    def __init__(self, logger ):
        """ Sets up basics. """
        self.DB_HOST = settings.DB_HOST
        self.DB_PORT = settings.DB_PORT
        self.DB_USERNAME = settings.DB_USERNAME
        self.DB_PASSWORD = settings.DB_PASSWORD
        self.DB_NAME = settings.DB_NAME
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
            raise Exception( unicode(repr(e)) )
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
            raise Exception( unicode(repr(e)) )

    def _run_execute( self, sql ):
        """ Executes select; returns tuple of row-dicts.
            Example return data: ( {row1field1key: row1field1value, row1field2key: row1field2value}, {row2field1key: row2field1value, row2field2key: row2field2value} )
            Called by run_select() """
        self.cursor_object.execute( sql )
        dict_list = self.cursor_object.fetchall()  # really a tuple of row-dicts
        self.logger.debug( u'dict_list, ```%s```' % pprint.pformat(dict_list) )
        return dict_list

    def _unicodify_resultset( self, dict_list ):
        """ Ensures result-set's keys & values are unicode-strings.
            Called by run_select() """
        try:
            result_list = []
            for row_dict in dict_list:
                new_row_dict = {}
                for key,value in row_dict.items():
                    new_row_dict[ unicode(key) ] = self._unicodify_value( value )
                result_list.append( new_row_dict )
            return result_list
        except Exception as e:
            self.logger.error( u'error: %s' % unicode(repr(e).decode(u'utf8', u'replace')) )
            raise Exception( unicode(repr(e)) )

    def _unicodify_value( self, value ):
        """ Ensures value is unicode.
            Called by _unicodify_value() """
        if type(value) in [ datetime.datetime, int, long ]:
            value = unicode(value)
        else:
            value = value.decode( 'utf-8', 'replace' )
        return value

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

  # end class DB_Handler()
