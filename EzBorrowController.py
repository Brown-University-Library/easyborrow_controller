# -*- coding: utf-8 -*-

'''
- Purpose: this script directs calls to the tunnelers,
  updates logging and history tables, and sends user and staff emails.
- Called by: cron script running every two minutes.
'''

import os  #  interesting -- the import os in the try below is needed



class Controller:



  def runCode(self):

    try:
      #######
      # setup environment
      #######

      import os

      MYSQL_DIRECTORY_PATH = unicode( os.environ[u'ezbCTL__MYSQL_DIRECTORY_PATH'] )
      EASYBORROW_SCRIPTS_PATH = unicode( os.environ[u'ezbCTL__EASYBORROW_SCRIPTS_PATH'] )
      SELECT_SQL = unicode( os.environ[u'ezbCTL__SELECT_SQL'] )

      # pathwork
      import os, sys
      mainDirectoryPath = os.path.abspath('')
      sys.path.append( mainDirectoryPath + '/classes/' )  # will eventually get rid of this
      sys.path.append( MYSQL_DIRECTORY_PATH ) # not sure if this is necessary
      sys.path.append( EASYBORROW_SCRIPTS_PATH ) # to call inRhode code, until it can be made into a webservice

      # add enclosing directory to path
      current_script_name = sys.argv[0] # may or may not include path
      directory_path = os.path.dirname( current_script_name )
      full_directory_path = os.path.abspath( directory_path )
      directory_list = full_directory_path.split('/')
      last_element_string = directory_list[-1]
      enclosing_directory = full_directory_path.replace( '/' + last_element_string, '' ) # strip off the slash plus the current directory
      sys.path.append( enclosing_directory )

      #######
      # remaining imports
      #######

      # from django.utils import simplejson
      from easyborrow_controller_code import settings
      from easyborrow_controller_code import utility_code
      from easyborrow_controller_code.classes import Item
      from easyborrow_controller_code.classes import UtilityCode
      import json, pprint, string, sys

      itemInstance = Item.Item()
      utCdInstance = UtilityCode.UtilityCode()

      temp_identifier = utility_code.makeIdentifier()  # used until request-number is obtained
      log_identifier = temp_identifier  # log_identifier used in newer utility_code.updateLog()
      dateAndTimeText = utCdInstance.obtainDate()
      utCdInstance.updateLog( message='EZBorrowController session starting at %s' % dateAndTimeText, identifier=temp_identifier, message_importance='high' )

      #######
      # check for a request-record
      #######

      utCdInstance.updateLog( message='- in controller; checking for request-record...', identifier=temp_identifier, message_importance='low' )
      resultInfo = utCdInstance.connectExecuteSelect( SELECT_SQL ) ## [ [fieldname01, fieldname02], ( (row01field01_value, row01field02_value), (row02field01_value, row02field02_value) ) ]
      if( resultInfo == None ):
        utCdInstance.updateLog( message='- in controller; no new request found; quitting', identifier=temp_identifier, message_importance='high' )
        sys.exit()

      #######
      # gather info on request and update tables
      # (we won't get here if no record was found)
      #######

      # setup data

      itemInstance.fillFromDbRow(resultInfo)
      eb_request_number = itemInstance.itemDbId
      log_identifier = eb_request_number  # used in newer utility_code.updateLog()
      utCdInstance.updateLog( message='- in controller; record grabbed: %s' % resultInfo, message_importance='high', identifier='was_%s_now_%s' % (temp_identifier, eb_request_number) )

      # update request and history tables

      itemInstance.updateRequestStatus("in_process")
      itemInstance.updateHistoryNote( "Processing started" )

      #######
      # process flow
      #######

      flowList = itemInstance.determineFlow()
      utility_code.updateLog( u'- in controller; flowList is: %s' % flowList, log_identifier, message_importance=u'high' )

      flowString = string.join( flowList, ', ' )
      itemInstance.updateHistoryNote( "Flow: %s" % flowString )

      for service in flowList:

        if (service == 'ir'):

          ##
          ## send a request to InRhode
          ##

          itemInstance.currentlyActiveService = 'inRhode'

          utCdInstance.updateLog( message='- in controller; checking InRhode...', message_importance='high', identifier=eb_request_number )
          try:
            inRhodeResultData = itemInstance.checkInRhode(eb_request_number)
          except Exception, e:
            print 'checkInRhode() failed, exception is: %s' % e
          # inRhodeResultData = itemInstance.checkInRhode()

          # examine InRhode results
          try:
            utCdInstance.updateLog( message='- in controller; InRhode resultData: %s' % inRhodeResultData, message_importance='high', identifier=eb_request_number )
          except Exception, e:
            print 'updateLog() showing inrhode resultData failed, exception is: %s' % e
          # utCdInstance.updateLog( message='- InRhode resultData: %s' % inRhodeResultData, message_importance='high', identifier=eb_request_number )
          inRhodeStatus = inRhodeResultData # simple string
          utCdInstance.updateLog( message='- in controller; InRhode status: %s' % inRhodeStatus, message_importance='high', identifier=eb_request_number )

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

          from easyborrow_controller_code.classes.tunneler_runners import BD_Runner

          itemInstance.currentlyActiveService = u'borrowDirect'
          utCdInstance.updateLog( message='- in controller; checking BorrowDirect...', message_importance='high', identifier=eb_request_number )

          if type(eb_request_number) == int:
            eb_request_number = unicode( eb_request_number )
          if type(itemInstance.patronBarcode) == str:
            itemInstance.patronBarcode = itemInstance.patronBarcode.decode( u'utf-8', u'replace' )
          if type(itemInstance.itemIsbn) == str:
            itemInstance.itemIsbn = itemInstance.itemIsbn.decode( u'utf-8', u'replace' )
          if type(itemInstance.sfxurl) == str:
            itemInstance.sfxurl = itemInstance.sfxurl.decode( u'utf-8', u'replace' )

          # print u'- settings.BD_API_URL:'; print settings.BD_API_URL
          # print u'- settings.OPENURL_PARSER_URL:'; print settings.OPENURL_PARSER_URL

          bd_data = {
            u'EB_REQUEST_NUM': eb_request_number,
            u'API_URL': settings.BD_API_URL,
            u'API_AUTH_CODE': settings.BD_API_AUTHORIZATION_CODE,
            u'API_IDENTITY': settings.BD_API_IDENTITY,
            u'UNIVERSITY': settings.BD_UNIVERSITY,
            u'USER_BARCODE': itemInstance.patronBarcode,
            u'ISBN': itemInstance.itemIsbn,
            u'WC_URL': itemInstance.sfxurl,
            u'OPENURL_PARSER_URL': settings.OPENURL_PARSER_URL,
            u'UC_INSTANCE': utCdInstance,  # for logging
            }
          bd_runner = BD_Runner( bd_data )
          bd_runner.determineSearchType()
          bd_runner.prepRequestData()
          if bd_runner.prepared_data_dict == u'skip_to_illiad':  # neither isbn nor good string
            bd_runner.updateHistoryTable()
          else:
            try:  # ensures bd problem doesn't hang full request processing
              bd_runner.requestItem()
            except Exception, e:
              bd_runner.api_result == u'FAILURE'  # eventually change this to u'ERROR' after updating code that acts on u'FAILURE'
            bd_runner.updateHistoryTable()
            if bd_runner.api_result == u'SUCCESS':
              ## return to existing flow
              itemInstance.requestSuccessStatus = u'success'
              itemInstance.genericAssignedUserEmail = itemInstance.patronEmail
              itemInstance.genericAssignedReferenceNumber = bd_runner.api_confirmation_code
              break  # out of the for-loop

        # elif(service == "bd"):
        #
        #   ##
        #   ## send a request to BorrowDirect
        #   ##
        #
        #   itemInstance.currentlyActiveService = "borrowDirect"
        #
        #   utCdInstance.updateLog( message='- in controller; checking BorrowDirect...', message_importance='high', identifier=eb_request_number )
        #   borrowDirectResultData = itemInstance.checkBorrowDirect( eb_request_number )
        #
        #   # examine BorrowDirect results
        #   utCdInstance.updateLog( message="- in controller; borrowDirect resultData: '%s'" % (borrowDirectResultData), message_importance='high', identifier=eb_request_number ) # added 2007-06-23-Saturday
        #   try:
        #     borrowDirectStatus = itemInstance.parseBorrowDirectResultData( borrowDirectResultData, eb_request_number )
        #   except Exception, e:
        #     utCdInstance.updateLog( message='- in controller; error on parsing BD status: %s' % e, message_importance='high', identifier=eb_request_number )
        #     pass
        #   utCdInstance.updateLog( message="- in controller; borrowDirect status: '%s'" % (borrowDirectStatus), message_importance='high', identifier=eb_request_number )
        #
        #   # update history table
        #
        #   if( borrowDirectStatus == "Request_Successful" ):
        #     parameterDict = {'serviceName':'borrowdirect', 'action':'attempt', 'result':borrowDirectStatus, 'number':itemInstance.borrowDirectAssignedReferenceNumber}
        #   else:
        #     parameterDict = {'serviceName':'borrowdirect', 'action':'attempt', 'result':borrowDirectStatus, 'number':''}
        #   itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )
        #
        #   # end section
        #
        #   if( borrowDirectStatus == "Request_Successful" ):
        #     itemInstance.requestSuccessStatus = "success"
        #     itemInstance.genericAssignedUserEmail = itemInstance.patronEmail
        #     itemInstance.genericAssignedReferenceNumber = 'N.A.'
        #     # itemInstance.genericAssignedUserEmail = itemInstance.borrowDirectAssignedUserEmail  # because bd-api is not yet capturing email
        #     itemInstance.genericAssignedReferenceNumber = itemInstance.borrowDirectAssignedReferenceNumber  # because bd-api is not yet caturing the assigned reference number
        #     break # break out of the 'for' loop

        elif(service == "vc"):

          ##
          ## send request to VirtualCatalog if necessary
          ##

          itemInstance.currentlyActiveService = "virtualCatalog"

          utCdInstance.updateLog( message='- in controller; checking VirtualCatalog...', message_importance='high', identifier=eb_request_number )
          virtualCatalogResultData = itemInstance.checkVirtualCatalog()

          # examine VirtualCatalog results

          virtualCatalogStatus = itemInstance.parseVirtualCatalogResultData(virtualCatalogResultData)
          utCdInstance.updateLog( message="- in controller; virtualCatalog status: '%s'" % virtualCatalogStatus, message_importance='high', identifier=eb_request_number )

          # update history table

          if( virtualCatalogStatus == "Request_Successful" ):
            parameterDict = {'serviceName':'virtualcatalog', 'action':'attempt', 'result':virtualCatalogStatus, 'number':itemInstance.virtualCatalogAssignedReferenceNumber}
          else:
            parameterDict = {'serviceName':'virtualcatalog', 'action':'attempt', 'result':virtualCatalogStatus, 'number':''}
          itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )

          # end section

          if( virtualCatalogStatus == "Request_Successful" ):
            itemInstance.requestSuccessStatus = "success"
            itemInstance.genericAssignedUserEmail = itemInstance.virtualCatalogAssignedUserEmail
            itemInstance.genericAssignedReferenceNumber = itemInstance.virtualCatalogAssignedReferenceNumber
            break # break out of the 'for' loop

        elif service == 'illiad':
          utility_code.updateLog( u'- in controller; service is now illiad', log_identifier )
          illiad_switch = settings.ILLIAD_REMOTEAUTH_SWITCH
          utility_code.updateLog( u'- in controller; illiad_switch is: %s' % illiad_switch, log_identifier )
          if illiad_switch == u'old_code':
            old_illiad_flow_result = utility_code.oldIlliadControllerFlow( eb_request_number, itemInstance, settings, utCdInstance )
            if type(old_illiad_flow_result) == dict:
              if u'status' in old_illiad_flow_result:
                if old_illiad_flow_result[u'status'] == u'failure':
                  return old_illiad_flow_result  # includes message key & value
          if illiad_switch == u'new_code':
            itemInstance.currentlyActiveService = "illiad"
            ## prepare parameters
            prep_result_dict = utility_code.makeIlliadParametersV2( itemInstance, settings, log_identifier )
            ## send request to illiad
            send_result_dict = utility_code.submitIlliadRemoteAuthRequestV2( prep_result_dict[u'parameter_dict'], log_identifier )
            ## evaluate result (update itemInstance, & history & request tables)
            eval_result_dict = utility_code.evaluateIlliadSubmissionV2( itemInstance, send_result_dict, log_identifier )

      # end of '''for service in flowList:'''

      #######
      # update 'requests' table & send email on success ('for' loop is over)
      #######

      utCdInstance.updateLog( message="- in controller; itemInstance.requestSuccessStatus is: %s" % itemInstance.requestSuccessStatus, message_importance='high', identifier=eb_request_number )

      if( itemInstance.requestSuccessStatus == "success" ):
        itemInstance.updateRequestStatus("processed")
        utCdInstance.updateLog( message="- in controller; request successful; preparing to send email", message_importance='high', identifier=eb_request_number )
        utCdInstance.sendEmail( itemInstance, eb_request_number )

      elif( itemInstance.requestSuccessStatus == "create_illiad_user_failed" ):
        # itemInstance.updateRequestStatus("processed") -- No, let's leave it as in_process so we get that 'try_again' button
        utCdInstance.updateLog( message="- in controller; create_illiad_user_failed detected; preparing to send email to staff", message_importance='high', identifier=eb_request_number )
        utCdInstance.sendEmail( itemInstance, eb_request_number )
        parameterDict = {'serviceName':'illiad', 'action':'followup', 'result':'ill_staff_emailed', 'number':''}
        itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )

      elif( itemInstance.requestSuccessStatus == 'login_failed_possibly_blocked' ):
        utility_code.updateLog( '- in controller; "blocked" detected; will send user email', log_identifier, message_importance='high' )
        result_dict = utility_code.makeEbRequest( itemInstance, log_identifier )  # eb_request is a storage-object; NOTE: as code is migrated toward newer architecture; this line will occur near beginning of runCode()
        utility_code.updateLog( '- in controller; eb_request obtained', log_identifier )
        result_dict = utility_code.sendEmail( result_dict['eb_request'], log_identifier )
        utility_code.updateLog( '- in controller; "blocked" detected; sendEmail() was called', log_identifier, message_importance='high' )
        #
        parameterDict = {'serviceName':'illiad', 'action':'followup', 'result':'blocked_user_emailed', 'number':''}
        itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )
        #
        if result_dict['status'] == 'success':
          itemInstance.updateRequestStatus("illiad_block_user_emailed")

      elif( itemInstance.requestSuccessStatus == "failure_no_sfx-link_to_illiad" ):
        itemInstance.updateRequestStatus("processed")
        utCdInstance.updateLog( message="- in controller; illiad 'no sfx link' message detected; preparing to send email to staff", message_importance='high', identifier=eb_request_number )
        utCdInstance.sendEmail( itemInstance, eb_request_number )
        parameterDict = {'serviceName':'illiad', 'action':'followup', 'result':'ill_staff_emailed', 'number':''}
        itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )

      elif( itemInstance.requestSuccessStatus == "unknown_illiad_failure" ):
  #     itemInstance.updateRequestStatus("processed")
        utCdInstance.updateLog( message="- in controller; illiad request #2 failed for unknown reason", message_importance='high', identifier=eb_request_number )
        utCdInstance.sendEmail( itemInstance, eb_request_number )
        parameterDict = {'serviceName':'illiad', 'action':'followup', 'result':'admin_emailed', 'number':''}
        itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )

      else:
        utCdInstance.updateLog( message="- in controller; unknown itemInstance.requestSuccessStatus; it is: %s" % itemInstance.requestSuccessStatus, message_importance='high', identifier=eb_request_number )
        utCdInstance.sendEmail( itemInstance, eb_request_number )
        parameterDict = {'serviceName':'illiad', 'action':'followup', 'result':'admin_emailed', 'number':''}
        itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )

      #######
      # end process
      #######

    except SystemExit:
      pass
      # utility_code.updateLog( '- in controller; quitting', log_identifier=log_identifier, message_importance='high' )
    except:
      try:
        import sys
        err_msg = u'error-type - %s; error-message-a - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, )
        print err_msg
        error_message = utility_code.makeErrorString()
        utility_code.updateLog( '- in controller; EXCEPTION; error: %s' % repr(error_message), log_identifier='exception', message_importance='high' )
      except Exception, e:
        print 'ezb controller exception: %s' % e

        import sys
        err_msg = u'error-type - %s; error-message - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, )
        print err_msg

        # self.endProgram()



  def endProgram(self):

    import sys

    sys.exit()



if __name__ == "__main__":
  ## setup
  from easyborrow_project_local_settings.eb_controller_local_settings import settings_local as controller_settings
  activate_this = '%s/bin/activate_this.py' % controller_settings.PROJECT_ENV_DIR_PATH
  execfile( activate_this, dict(__file__=activate_this) )
  ## run controller
  controllerInstance = Controller()
  controllerInstance.runCode()

