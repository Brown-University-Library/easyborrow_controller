import datetime, logging, pprint
import MySQLdb
from easyborrow_controller_code import settings


LOG_PATH = settings.LOG_PATH
LOG_LEVEL = settings.LOG_LEVEL
level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
logger = logging.getLogger(__name__)


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
        self.hist_action_sql = settings.HISTORY_ACTION_SQL
        self.logger = logger
        self.logger.debug( 'DB_Handler instantiated' )

    ## main functions ##

    def run_select( self, sql ):
        """ Executes sql, returns key-value dict.
            Called by controller.run_record_search() """
        logger.debug( f'sql, ``{sql}``' )
        try:
            dict_list = None
            self._setup_db_connection()
            if self.cursor_object:
                dict_list = self._run_execute( sql )
                dict_list = self._unicodify_resultset( dict_list )
            return dict_list
        except Exception as e:
            err = repr( e )
            self.logger.error( 'error: %s' % err )
            raise Exception( err )
        finally:
            self._close_db_connection()

    def run_sql( self, sql ):
        """ Executes sql; returns nothing.
            Called by, initially, tunneler_runners.BD_ApiRunner.update_history_table() """
        if type( sql ) == str:
            sql = sql.encode( 'utf-8' )
        try:
            self._setup_db_connection()
            self.cursor_object.execute( sql )

            self.connection_object.commit()  ## needed for innodb tables!!

        except Exception as e:
            err = repr( e )
            self.logger.error( 'error: %s' % err )
            raise Exception( err )
        finally:
            self._close_db_connection()
        return

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
            err = repr( e )
            self.logger.error( 'error: %s' % err )
            raise Exception( err )

    def _run_execute( self, sql ):
        """ Executes select; returns tuple of row-dicts.
            Example return data: ( {row1field1key: row1field1value, row1field2key: row1field2value}, {row2field1key: row2field1value, row2field2key: row2field2value} )
            Called by run_select() """
        self.cursor_object.execute( sql )
        dict_list = self.cursor_object.fetchall()  # really a tuple of row-dicts
        self.logger.debug( 'dict_list, ```%s```' % pprint.pformat(dict_list) )
        return dict_list

    def _unicodify_resultset( self, dict_list ):
        """ Ensures result-set's keys & values are unicode-strings.
            Called by run_select() """
        try:
            result_list = []
            for row_dict in dict_list:
                new_row_dict = {}
                for key, value in row_dict.items():
                    new_row_dict[ str(key) ] = self._unicodify_value( value )
                result_list.append( new_row_dict )
            return result_list
        except Exception as e:
            err = repr( e )
            self.logger.error( 'error: %s' % err )
            raise Exception( err)


    def _unicodify_value( self, value ):
        """ Ensures value is a unicode string.
            Called by _unicodify_value() """
        if type(value) == str:
            pass
        elif type(value) in [ datetime.datetime, int ]:
            value = str(value)
        else:
            log.warning( f'unhandled type of, ``{type(value)}``' )
        return value

    # def _unicodify_value( self, value ):
    #     """ Ensures value is unicode.
    #         Called by _unicodify_value() """
    #     if type(value) in [ datetime.datetime, int, long ]:
    #         value = unicode(value)
    #     else:
    #         value = value.decode( 'utf-8', 'replace' )
    #     return value

    def _close_db_connection( self ):
        """ Closes db connection.
            Called by run_select() """
        try:
            self.cursor_object.close()
            self.connection_object.close()
            self.logger.debug( 'db connection closed' )
            return
        except Exception as e:
            err = repr( e )
            self.logger.error( 'error: %s' % err )

    ## end class DB_Handler()
