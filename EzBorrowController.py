# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
- Purpose:
  - directs calls to the tunnelers
  - updates logging and history tables
  - sends user and staff emails
- Called by: cron script running every two minutes.
- Assumes:
  - virtual environment set up
  - site-packages `requirements.pth` file adds settings directory and easyborrow_controller_code-enclosing-directory to sys path.
  - env/bin/activate file sources settings
"""

import datetime, json, logging, os, pprint, random, string, sys, time
from easyborrow_controller_code import settings, utility_code
# from easyborrow_controller_code.classes import db_handler, UtilityCode
from easyborrow_controller_code.classes import db_handler
from easyborrow_controller_code.classes.basics import Request_Meta as Request_Obj, Patron as Patron_Obj, Item as Item_Obj
from easyborrow_controller_code.classes.emailer import MailBuilder, Mailer
from easyborrow_controller_code.classes.tunneler_runners import BD_ApiRunner, IlliadApiRunner
from easyborrow_controller_code.classes.web_logger import WebLogger


## set up file logger
LOG_PATH = settings.LOG_PATH
LOG_LEVEL = settings.LOG_LEVEL
level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
logger = logging.getLogger(__name__)
logger.info( 'controller log started' )


## prevent modules from unnecessary logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


## some instantiations
request_inst = Request_Obj()
patron_inst = Patron_Obj()
item_inst = Item_Obj()


## get to work
class Controller( object ):

    def __init__( self ):
        """ Grabs settings from environment and sets up logger.
            Note: SQL attributes are pattern-statements; string-substitution completes them. """
        self.SELECT_SQL = settings.CONTROLLER_SELECT_SQL
        self.HISTORY_NOTE_SQL = settings.HISTORY_NOTE_SQL
        self.HISTORY_ACTION_SQL = settings.HISTORY_ACTION_SQL
        self.REQUEST_UPDATE_SQL = settings.REQUEST_UPDATE_SQL
        self.log_identifier = 'temp--%s--%s' % ( datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), random.randint(1000,9999) )    # will be ezb-request-number: helps track which log-entries go with which request
        self.db_handler = None

    def run_code( self ):
        """ Coordinates processing.
            Called by `if __name__ == '__main__':` """

        try:

            #######
            # setup
            #######

            # ( utCdInstance, web_logger ) = self.setup()
            web_logger = self.setup()

            #######
            # check for a request-record
            #######

            record_search = self.run_record_search( web_logger )

            #######
            # set identifier
            #######

            eb_request_number = self.set_identifier( record_search, web_logger )  # also updates self.log_identifier
            # utCdInstance.log_identifier = eb_request_number

            #######
            # gather info on request and update tables
            # (we won't get here if no record was found)
            #######

            # setup data
            ( request_inst, patron_inst, item_inst ) = self.fill_from_db_row( record_search )
            logger.debug( 'item_inst.volumes_info, `%s`' % item_inst.volumes_info )
            logger.debug( 'item_inst.isbn, `%s`' % item_inst.isbn )

            # update request and history tables
            self.update_request_status( 'in_process', eb_request_number )
            self.update_history_note( eb_request_number, 'Processing started' )

            #######
            # process flow
            #######

            flow_list = self.determine_flow( item_inst )
            web_logger.post_message( message='- in controller; flow_list is: %s' % flow_list, identifier=self.log_identifier, importance='info' )

            flow_string = string.join( flow_list, ', ' )
            self.update_history_note( eb_request_number, 'Flow: %s' % flow_string )

            for service in flow_list:

                if (service == 'ir'):
                    pass

                elif(service == "bd"):

                    ##
                    ## send a request to BorrowDirect
                    ##

                    # setup
                    bd_api_runner = BD_ApiRunner( logger, self.log_identifier )
                    request_inst.current_service = 'borrowDirect'
                    item_inst = bd_api_runner.setup_api_hit( item_inst, web_logger )

                    # prepare data
                    bd_data = bd_api_runner.prepare_params( patron_inst, item_inst )

                    # hit api
                    bd_api_runner.hit_bd_api( bd_data['isbn'], bd_data['user_barcode'] )  # response in bd_api_runner.bdpyweb_response_dct

                    # normalize response
                    bd_api_runner.process_response()  # populates class attributes api_confirmation_code, api_found, & api_requestable

                    # update history table
                    bd_api_runner.update_history_table()  # uses new classes/db_handler.py code

                    # handle success (processing just continues if request not successful)
                    if bd_api_runner.api_requestable == True:
                        request_inst = bd_api_runner.handle_success( request_inst )
                        break

                elif(service == "vc"):
                    pass

                elif service == 'illiad':
                    web_logger.post_message( message='- in controller; service is now illiad', identifier=self.log_identifier, importance='info' )
                    illiad_api_runner = IlliadApiRunner( request_inst )
                    request_inst.current_service = 'illiad'
                    prep_result_dct = illiad_api_runner.make_parameters( request_inst, patron_inst, item_inst )  # prepare parameters
                    send_result_dct = illiad_api_runner.submit_request( prep_result_dct['parameter_dict'] )  # send request to illiad
                    request_inst = illiad_api_runner.evaluate_response( request_inst, send_result_dct )  # updates request_inst and history note; updated request_inst not yet used

            # end of '''for service in flow_list:'''

            #######
            # update 'requests' table & send email on success ('for' loop is over)
            #######

            web_logger.post_message( message='- in controller; request_inst.current_status is: %s' % request_inst.current_status, identifier=self.log_identifier, importance='info' )

            if request_inst.current_status == 'success':
                self.update_request_status( 'processed', request_inst.request_number )
                web_logger.post_message( message='- in controller; request successful; preparing to send email', identifier=self.log_identifier, importance='info' )
                self.deliver_mail( request_inst, patron_inst, item_inst )

            elif( request_inst.current_status == 'login_failed_possibly_blocked' ):
                web_logger.post_message( message='- in controller; "blocked" detected; will send user email', identifier=self.log_identifier, importance='info' )
                delivered = self.deliver_mail( request_inst, patron_inst, item_inst )
                if delivered is True:
                    web_logger.post_message( message='- in controller; "blocked" detected; email sent', identifier=self.log_identifier, importance='info' )
                    self.update_history_action( eb_request_number, 'illiad', 'followup', 'blocked_user_emailed', '' )  # request_num, service, action, result, transaction_num
                    self.update_request_status( 'illiad_block_user_emailed', request_inst.request_number )

            else:
                web_logger.post_message( message='- in controller; unknown request_inst.current_status; it is: %s' % request_inst.current_status, identifier=self.log_identifier, importance='info' )
                self.deliver_mail( request_inst, patron_inst, item_inst )
                self.update_history_action( request_inst.request_number, 'illiad?', 'problem', 'admin_emailed', '' )  # request_num, service, action, result, transaction_num

            #######
            # end process
            #######

        except SystemExit:
            pass

        except Exception as e:
            logger.error( 'exception, %s' % unicode(repr(e)) )
            err_msg = 'error-type - %s; error-message - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, )
            logger.error( 'detailed exception, %s' % unicode(repr(err_msg)) )
            web_logger.post_message( message='- in controller; EXCEPTION; error: %s' % unicode(repr(err_msg)), identifier=self.log_identifier, importance='error' )
            print err_msg

        ## end def run_code()

    ## helper functions called by run_code() ##

    def deliver_mail( self, request_inst, patron_inst, item_inst ):
        """ Calls MailBuilder() and Mailer().
            Returns boolean.
            Called by run_code() """
        mail_builder = MailBuilder( request_inst, patron_inst, item_inst )
        mail_builder.prep_email()
        mailer = Mailer( mail_builder.to, mail_builder.reply_to, mail_builder.subject, mail_builder.message, request_inst.request_number  )
        rslt = mailer.send_email()
        return rslt

    def setup( self ):
        """ Calls initial weblog entry and returns class instances.
            Called by run_code() """
        try:
            self.db_handler = db_handler.Db_Handler( logger )
        except Exception as e:
            logger.error( 'e, `%s`' % e )
        # utCdInstance = UtilityCode.UtilityCode( logger )
        web_logger = WebLogger( logger )
        formatted_time = time.strftime( '%a %b %d %H:%M:%S %Z %Y', time.localtime() )  # eg 'Wed Jul 13 13:41:39 EDT 2005'
        web_logger.post_message( message='EZBorrowController session starting at %s' % formatted_time, identifier=self.log_identifier, importance='info' )
        logger.debug( 'setup() complete' )
        # return ( utCdInstance, web_logger )
        return web_logger

    def run_record_search( self, web_logger ):
        """ Searches for new request.
            Called by run_code() """
        result_dcts = self.db_handler.run_select( self.SELECT_SQL )  # [ {row01field01_key: row01field01_value}, fieldname02], ( (row01field01_value, row01field02_value), (row02field01_value, row02field02_value) ) ]
        logger.debug( '(new) record_search, `%s`' % result_dcts )
        if not result_dcts:
            web_logger.post_message( message='- in controller; no new request found; quitting', identifier=self.log_identifier, importance='info' )
            logger.info( 'no new record; quitting' )
            sys.exit()
        record_search = result_dcts[0]
        web_logger.post_message( message='- in controller; new request found, ```%s```' % pprint.pformat(record_search), identifier=self.log_identifier, importance='info' )
        return record_search

    def set_identifier( self, record_search, web_logger ):
        """ Sets the identifier with the db id.
            Called by run_code() """
        eb_request_number = record_search['id']
        web_logger.post_message( message='- in controller; updating identifier', identifier='was_%s_now_%s' % (self.log_identifier, eb_request_number), importance='info' )
        self.log_identifier = record_search['id']
        return eb_request_number

    def fill_from_db_row( self, db_dct ):
        """ Updates attributes from found record data.
            Note: db_dct contains more data; just storing what's needed.
            Called by run_code() """
        request_inst.request_number = db_dct['id']
        patron_inst.firstname = db_dct['firstname'].strip()
        patron_inst.lastname = db_dct['lastname'].strip()
        patron_inst.eppn = db_dct['eppn'].strip()  # really just the username part
        patron_inst.barcode = db_dct['barcode']
        patron_inst.email = db_dct['email']
        item_inst.title = db_dct['title']
        item_inst.isbn = db_dct['isbn']
        item_inst.oclc_num = db_dct['wc_accession']
        item_inst.volumes_info = db_dct['volumes']
        item_inst.knowledgebase_openurl = db_dct['sfxurl']
        return ( request_inst, patron_inst, item_inst )

    def update_history_note( self, request_id, note ):
        """ Updates history note, either that processing has started, or what the flow is.
            Called by run_code() """
        try:
            sql = self.HISTORY_NOTE_SQL % ( request_id, note )
            logger.debug( 'update_history_note sql, `%s`' % sql )
            self.db_handler.run_sql( sql )
        except Exception as e:
            logger.error( 'update_history_note error, ```%s```' % unicode(repr(e)) )
        return

    def determine_flow( self, item_inst ):
        """ Determines services to try, and order.
            No longer allows for BorrowDirect string requesting since new API doesn't permit it.
            Called by run_code() """
        flow = [ 'illiad' ]
        if len( item_inst.volumes_info ) == 0:
            if len( item_inst.isbn ) > 0:
                flow = [ 'bd', 'illiad' ]
        logger.debug( 'determine_flow() result, `%s`' % flow )
        return flow

    def update_history_action( self, request_id, service_name, action, result, number ):
        """ Updates history table's service name-action-result info.
            Called by run_code() """
        try:
            sql = self.HISTORY_ACTION_SQL % ( request_id, service_name, action, result, number )
            logger.debug( 'update_history_action sql, `%s`' % sql )
            self.db_handler.run_sql( sql )
        except Exception as e:
            logger.error( 'update_history_action error, ```%s```' % unicode(repr(e)) )
        return

    def update_request_status( self, new_status, request_id ):
        """ Updates request table's status info.
            Called by run_code() """
        try:
            sql = self.REQUEST_UPDATE_SQL % ( new_status, request_id )
            logger.debug( 'update_request_status sql, `%s`' % sql )
            self.db_handler.run_sql( sql )
        except Exception as e:
            logger.error( 'update_request_status error, ```%s```' % unicode(repr(e)) )
            raise Exception( unicode(repr(e)) )
        return

    # end class Controller




if __name__ == '__main__':
    controller_instance = Controller()
    controller_instance.run_code()
