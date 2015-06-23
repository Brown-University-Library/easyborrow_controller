# -*- coding: utf-8 -*-

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
from easyborrow_controller_code.classes import db_handler, Item, UtilityCode
from easyborrow_controller_code.classes.tunneler_runners import BD_Runner, BD_ApiRunner
from easyborrow_controller_code.classes.web_logger import WebLogger


class Controller( object ):

    def __init__( self ):
        """ Grabs settings from environment and sets up logger. """
        self.SELECT_SQL = unicode( os.environ[u'ezbCTL__SELECT_SQL'] )
        self.LOG_PATH = unicode( os.environ[u'ezbCTL__LOG_PATH'] )
        self.LOG_LEVEL = unicode( os.environ[u'ezbCTL__LOG_LEVEL'] )
        self.logger = None
        self.log_identifier = u'temp--%s--%s' % ( datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), random.randint(1000,9999) )    # will be ezb-request-number: helps track which log-entries go with which request
        self.setup_logger()

    def setup_logger( self ):
        """ Configures log path and level.
            Called by __init__() """
        log_level = { u'DEBUG': logging.DEBUG, u'INFO': logging.INFO }
        logging.basicConfig(
            filename=self.LOG_PATH, level=log_level[self.LOG_LEVEL],
            format=u'[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
            datefmt=u'%d/%b/%Y %H:%M:%S'
            )
        self.logger = logging.getLogger(__name__)
        self.logger.info( u'controller_instance instantiated' )
        return


    def run_code( self ):
        """ Coordinates processing.
            Called by `if __name__ == u'__main__':` """

        try:

            #######
            # setup
            #######

            ( dbh, itemInstance, utCdInstance, web_logger ) = self.setup()

            #######
            # check for a request-record
            #######

            record_search = self.run_record_search( dbh, web_logger )

            #######
            # set identifier
            #######

            eb_request_number = self.set_identifier( record_search, web_logger )  # also updates self.log_identifier
            itemInstance.log_identifier = eb_request_number
            utCdInstance.log_identifier = eb_request_number

            #######
            # gather info on request and update tables
            # (we won't get here if no record was found)
            #######

            # setup data
            itemInstance.fill_from_db_row( record_search )

            # update request and history tables
            itemInstance.updateRequestStatus("in_process")
            itemInstance.updateHistoryNote( "Processing started" )

            #######
            # process flow
            #######

            flowList = self.determine_flow( itemInstance )
            # utility_code.updateLog( u'- in controller; flowList is: %s' % flowList, self.log_identifier, message_importance=u'high' )
            web_logger.post_message( message=u'- in controller; flowList is: %s' % flowList, identifier=self.log_identifier, importance='info' )

            flowString = string.join( flowList, ', ' )
            itemInstance.updateHistoryNote( "Flow: %s" % flowString )

            for service in flowList:

                if (service == 'ir'):

                    ##
                    ## send a request to InRhode
                    ##

                    itemInstance.currentlyActiveService = 'inRhode'

                    web_logger.post_message( message=u'- in controller; checking InRhode...', identifier=self.log_identifier, importance='info' )
                    try:
                      inRhodeResultData = itemInstance.checkInRhode(eb_request_number)
                    except Exception, e:
                      print 'checkInRhode() failed, exception is: %s' % e

                    # examine InRhode results
                    try:
                      web_logger.post_message( message=u'- in controller; InRhode resultData: %s' % inRhodeResultData, identifier=self.log_identifier, importance='info' )
                    except Exception, e:
                      print 'updateLog() showing inrhode resultData failed, exception is: %s' % e
                    inRhodeStatus = inRhodeResultData # simple string
                    web_logger.post_message( message=u'- in controller; InRhode status: %s' % inRhodeStatus, identifier=self.log_identifier, importance='info' )
                    # update history table

                    parameterDict = {'serviceName':'inrhode', 'action':'attempt', 'result':inRhodeStatus, 'number':'N.A.'}
                    itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )

                    # end section

                    if ( inRhodeStatus == 'request_successful' ):
                      itemInstance.requestSuccessStatus = 'success'
                      itemInstance.genericAssignedUserEmail = itemInstance.patronEmail
                      itemInstance.genericAssignedReferenceNumber = 'N.A.'
                      break # out of the 'for' loop

                elif(service == "bd"):

                    ##
                    ## send a request to BorrowDirect
                    ##

                    # setup
                    bd_api_runner = BD_ApiRunner( self.logger, self.log_identifier )
                    itemInstance = bd_api_runner.setup_api_hit( itemInstance, web_logger )
                    # itemInstance = bd_api_runner.setup_api_hit( itemInstance, utCdInstance )

                    # prepare data
                    bd_data = bd_api_runner.prepare_params( itemInstance )

                    # hit api
                    bd_api_runner.hit_bd_api( bd_data[u'isbn'], bd_data[u'user_barcode'] )  # response in bd_api_runner.bdpyweb_response_dct

                    # normalize response
                    bd_api_runner.process_response()  # populates class attributes api_confirmation_code, api_found, & api_requestable

                    # update history table
                    bd_api_runner.update_history_table( utCdInstance )

                    # handle success (processing just continues if request not successful)
                    if bd_api_runner.api_requestable == True:
                        itemInstance = bd_api_runner.handle_success( itemInstance )
                        break

                elif(service == "vc"):

                    pass

                elif service == u'illiad':
                    # utility_code.updateLog( u'- in controller; service is now illiad', self.log_identifier )
                    web_logger.post_message( message=u'- in controller; service is now illiad', identifier=self.log_identifier, importance='info' )
                    itemInstance.currentlyActiveService = u'illiad'
                    prep_result_dict = utility_code.makeIlliadParametersV2( itemInstance, settings, self.log_identifier )  # prepare parameters
                    send_result_dict = utility_code.submitIlliadRemoteAuthRequestV2( prep_result_dict[u'parameter_dict'], self.log_identifier )  # send request to illiad
                    eval_result_dict = utility_code.evaluateIlliadSubmissionV2( itemInstance, send_result_dict, self.log_identifier )  # evaluate result (update itemInstance, & history & request tables)

            # end of '''for service in flowList:'''

            #######
            # update 'requests' table & send email on success ('for' loop is over)
            #######

            web_logger.post_message( message=u'- in controller; itemInstance.requestSuccessStatus is: %s' % itemInstance.requestSuccessStatus, identifier=self.log_identifier, importance='info' )

            if( itemInstance.requestSuccessStatus == "success" ):
              itemInstance.updateRequestStatus("processed")
              web_logger.post_message( message=u'- in controller; request successful; preparing to send email', identifier=self.log_identifier, importance='info' )
              utCdInstance.sendEmail( itemInstance, eb_request_number )

            elif( itemInstance.requestSuccessStatus == "create_illiad_user_failed" ):
              web_logger.post_message( message=u'- in controller; create_illiad_user_failed detected; preparing to send email to staff', identifier=self.log_identifier, importance='info' )
              utCdInstance.sendEmail( itemInstance, eb_request_number )
              parameterDict = {'serviceName':'illiad', 'action':'followup', 'result':'ill_staff_emailed', 'number':''}
              itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )

            elif( itemInstance.requestSuccessStatus == 'login_failed_possibly_blocked' ):
              web_logger.post_message( message=u'- in controller; "blocked" detected; will send user email', identifier=self.log_identifier, importance='info' )
              result_dict = utility_code.makeEbRequest( itemInstance, self.log_identifier )  # eb_request is a storage-object; NOTE: as code is migrated toward newer architecture; this line will occur near beginning of runCode()
              web_logger.post_message( message=u'- in controller; eb_request obtained', identifier=self.log_identifier, importance='info' )
              result_dict = utility_code.sendEmail( result_dict['eb_request'], self.log_identifier )
              web_logger.post_message( message=u'- in controller; "blocked" detected; sendEmail() was called', identifier=self.log_identifier, importance='info' )
              #
              parameterDict = {'serviceName':'illiad', 'action':'followup', 'result':'blocked_user_emailed', 'number':''}
              itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )
              #
              if result_dict['status'] == 'success':
                itemInstance.updateRequestStatus("illiad_block_user_emailed")

            elif( itemInstance.requestSuccessStatus == "failure_no_sfx-link_to_illiad" ):
              itemInstance.updateRequestStatus("processed")
              web_logger.post_message( message=u'- in controller; illiad "no sfx link" message detected; preparing to send email to staff', identifier=self.log_identifier, importance='info' )
              utCdInstance.sendEmail( itemInstance, eb_request_number )
              parameterDict = {'serviceName':'illiad', 'action':'followup', 'result':'ill_staff_emailed', 'number':''}
              itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )

            elif( itemInstance.requestSuccessStatus == "unknown_illiad_failure" ):
              web_logger.post_message( message=u'- in controller; illiad request #2 failed for unknown reason', identifier=self.log_identifier, importance='info' )
              utCdInstance.sendEmail( itemInstance, eb_request_number )
              parameterDict = {'serviceName':'illiad', 'action':'followup', 'result':'admin_emailed', 'number':''}
              itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )

            else:
              web_logger.post_message( message=u'- in controller; unknown itemInstance.requestSuccessStatus; it is: %s' % itemInstance.requestSuccessStatus, identifier=self.log_identifier, importance='info' )
              utCdInstance.sendEmail( itemInstance, eb_request_number )
              parameterDict = {'serviceName':'illiad', 'action':'followup', 'result':'admin_emailed', 'number':''}
              itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )

            #######
            # end process
            #######

        except SystemExit:
            pass
        except:
            try:
                  err_msg = u'error-type - %s; error-message-a - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, )
                  print err_msg
                  error_message = utility_code.makeErrorString()
                  self.logger.error( u'%s- exception message, `%s`' % (self.log_identifier, err_msg) )
                  web_logger.post_message( message=u'- in controller; EXCEPTION; error: %s' % unicode(repr(error_message)), identifier=self.log_identifier, importance='info' )
            except Exception, e:
                  print 'ezb controller exception: %s' % e
                  err_msg = u'error-type - %s; error-message - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, )
                  print err_msg
                  self.logger.error( u'%s- exception message, `%s`' % (self.log_identifier, err_msg) )

        # end def run_code()


    def setup( self ):
        """ Calls initial weblog entry and returns class instances.
            Called by run_code() """
        try:
            dbh = db_handler.Db_Handler( self.logger )
        except Exception as e:
            self.logger.error( u'e, `%s`' % e )
        itemInstance = Item.Item()
        utCdInstance = UtilityCode.UtilityCode()
        web_logger = WebLogger( self.logger )
        formatted_time = time.strftime( u'%a %b %d %H:%M:%S %Z %Y', time.localtime() )  # eg 'Wed Jul 13 13:41:39 EDT 2005'
        web_logger.post_message( message=u'EZBorrowController session starting at %s' % formatted_time, identifier=self.log_identifier, importance='info' )
        self.logger.debug( u'setup() complete' )
        return ( dbh, itemInstance, utCdInstance, web_logger )

    def run_record_search( self, dbh, web_logger ):
        """ Searches for new request.
            Called by run_code() """
        result_dcts = dbh.run_select( self.SELECT_SQL )  # [ {row01field01_key: row01field01_value}, fieldname02], ( (row01field01_value, row01field02_value), (row02field01_value, row02field02_value) ) ]
        self.logger.debug( u'(new) record_search, `%s`' % result_dcts )
        if not result_dcts:
            web_logger.post_message( message=u'- in controller; no new request found; quitting', identifier=self.log_identifier, importance='info' )
            self.logger.info( u'no new record; quitting' )
            sys.exit()
        record_search = result_dcts[0]
        web_logger.post_message( message=u'- in controller; new request found, ```%s```' % pprint.pformat(record_search), identifier=self.log_identifier, importance='info' )
        return record_search

    def set_identifier( self, record_search, web_logger ):
        """ Sets the identifier with the db id.
            Called by run_code() """
        eb_request_number = record_search['id']  # older identifier, still used
        web_logger.post_message( message=u'- in controller; updating identifier', identifier=u'was_%s_now_%s' % (self.log_identifier, eb_request_number), importance='info' )
        self.log_identifier = record_search['id']  # newer identifier
        return eb_request_number

    def determine_flow( self, itemInstance ):
        """ Determines services to try, and order.
            No longer allows for BorrowDirect string requesting since new API doesn't permit it.
            Called by run_code() """
        flow = [ u'illiad' ]
        if len( itemInstance.volumesPreference ) == 0:
            if len( itemInstance.itemIsbn ) > 0:
                flow = [ u'bd', u'ir', u'illiad' ] # changed on 2015-05-28 at request of BB email; was [ u'bd', u'illiad' ]
        self.logger.debug( u'determine_flow() complete' )
        return flow

    # end class Controller




if __name__ == u'__main__':
  controller_instance = Controller()
  controller_instance.run_code()
