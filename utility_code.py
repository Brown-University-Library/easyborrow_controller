# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, json, os, pprint, smtplib, sys, time, urllib, urllib2
import requests
from easyborrow_controller_code import settings
from easyborrow_controller_code.classes.web_logger import WebLogger


web_logger = WebLogger( logger )
# web_logger.post_message( message='the message', identifier=self.log_identifier, importance='info' )


class EB_Request:
  '''
  - Purpose: to serve as a storage object for item-info, patron-info, and request-info.
  - Called by: instance created by controller.runCode(); attributes populated by different functions.
  '''

  # item info
  item_title = ''
  item_oclc_number = ''

  # patron info
  patron_firstname = ''
  patron_lastname = ''
  patron_email = ''
  #
  patron_phone = ''
  patron_address = ''
  patron_status = ''
  patron_department = ''

  # request info
  request_ezb_reference_number = ''  # the easyBorrow id
  request_current_tunneler_service = ''
  request_current_tunneler_status = ''

  # end class EB_Request



def evaluateIlliadSubmissionV2( itemInstance, send_result_dict, log_identifier ):
  try:
    return_dict = { 'status': 'init' }
    ## new-user check
    if 'new_user' in send_result_dict:
      if send_result_dict['new_user'] == True:
        updateLog( '- in utility_code.evaluateIlliadSubmissionV2(); Illiad user created...', log_identifier, message_importance='high' )
        parameterDict = { 'serviceName': 'illiad', 'action': 'create_illiad_user_attempt', 'result': 'success', 'number': '' }
        itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )
    ## illiad status check
    if 'status' in send_result_dict:
      parameterDict = None  # for history update
      if send_result_dict['status'] == 'submission_successful':
        itemInstance.illiadAssignedReferenceNumber = send_result_dict['transaction_number']  # it should be there
        parameterDict = { 'serviceName': 'illiad', 'action': 'attempt', 'result': 'Request_Successful', 'number': itemInstance.illiadAssignedReferenceNumber }
        itemInstance.requestSuccessStatus = 'success'
        itemInstance.genericAssignedUserEmail = itemInstance.patronEmail
        itemInstance.genericAssignedReferenceNumber = itemInstance.illiadAssignedReferenceNumber
      elif send_result_dict['status'] == 'login_failed_possibly_blocked':
        itemInstance.requestSuccessStatus = 'login_failed_possibly_blocked'
        itemInstance.genericAssignedUserEmail = itemInstance.patronEmail
        patronInfo = itemInstance.grabPatronApiInfo(itemInstance.patronId)
        itemInstance.grabConvertedPatronApiInfo(patronInfo) # grabs converted info and stores it to attributes
      if parameterDict == None:
        parameterDict = { 'serviceName': 'illiad', 'action': 'attempt', 'result': send_result_dict['status'], 'number': '' }
      itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )
      return_dict['status'] = 'evaluation_successful'
    updateLog( '- in utility_code.evaluateIlliadSubmissionV2(); return_dict: %s' % return_dict, log_identifier, message_importance='high' )
    return return_dict
  except:
    message = '- in utility_code.evaluateIlliadSubmissionV2(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { 'error_message': message }



def jsonify(structure, rq_indent=2):
  '''
  - Purpose: serializes and formats non-model object in json.
  - Called by: multiple functions.
  '''
  data = json.dumps( structure, sort_keys=True, indent=rq_indent )
  return data
  # end def jsonify()



def makeOpenUrlSegment( initial_url, log_identifier ):
  try:
    if not type( initial_url ) == unicode:
      initial_url = unicode( initial_url )
    if not type( log_identifier ) == unicode:
      log_identifier = unicode( log_identifier )
    updateLog( '- in utility_code.makeOpenUrlSegment(); initial_url is: %s' % initial_url, log_identifier )
    parsed_url = initial_url[ initial_url.find( 'serialssolutions.com/?' ) + 22 : ]  # TODO: change this to use the urlparse library
    # parsed_url = initial_url[ initial_url.find( 'sid' ) : ]
    parsed_url = parsed_url.replace( 'genre=unknown', 'genre=book' )
    updateLog( '- in utility_code.makeOpenUrlSegment(); parsed_url is: %s' % parsed_url, log_identifier )
    return { 'openurl_segment': parsed_url }
  except:
    message = '- in utility_code.updateLog(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { 'status': 'failure', 'message': message }



def makeEbRequest( itemInstance, log_identifier ):
  '''
  - Purpose: temporary transitional hack while new controller architecture is slowly implemented; converts itemInstance to an EB_Request instance.
  - Called by: controller.runCode()
  '''
  try:
    eb_request = EB_Request()
    eb_request.patron_firstname = itemInstance.firstname
    eb_request.patron_lastname = itemInstance.lastname
    eb_request.patron_email = itemInstance.patronEmail
    eb_request.patron_phone = itemInstance.patron_api_telephone
    eb_request.patron_address = itemInstance.patron_api_address
    eb_request.patron_status = itemInstance.patronStatus
    eb_request.patron_department = itemInstance.patron_api_dept
    #
    eb_request.item_title = itemInstance.itemTitle
    eb_request.item_oclc_number = itemInstance.oclcNumber
    #
    eb_request.request_ezb_reference_number = log_identifier
    eb_request.request_current_tunneler_service = itemInstance.currentlyActiveService
    eb_request.request_current_tunneler_status = itemInstance.requestSuccessStatus
    #
    updateLog( '- in utility_code.makeEbRequest(); eb_request.__dict__ is: %s' % eb_request.__dict__, log_identifier )
    return_dict = { 'status': 'success', 'eb_request': eb_request }
    updateLog( '- in utility_code.makeEbRequest(); return_dict is: %s' % return_dict, log_identifier )
    return return_dict
  except:
    message = '- in utility_code.updateLog(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { 'status': 'failure', 'message': message }
  # end def makeEbRequest()



def makeErrorString():
  '''
  - Purpose: to return detailed error information for logging/debugging.
  - Called by: could be any exception block.
  '''

  return 'error-type - %s; error-message - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, )

  # end def makeErrorString()



def make_datetime_string():
  """ Returns time-string like 'Wed Oct 23 14:49:38 EDT 2013'. """
  time_object = time.localtime(); assert type(time_object) == time.struct_time
  time_string = time.strftime( '%a %b %d %H:%M:%S %Z %Y', time_object )
  return time_string



def makeIlliadParametersV2( itemInstance, settings, log_identifier ):
  try:
    updateLog( '- in utility_code.makeIlliadParametersV2(); starting...', log_identifier, message_importance='high' )  # TODO: lower hardcoded message_importance
    try:
      patron_info = itemInstance.grabPatronApiInfo( itemInstance.patronId )
      itemInstance.grabConvertedPatronApiInfo( patron_info) # grabs converted info and stores it to attributes
      updateLog( '- in utility_code.makeIlliadParametersV2(); patron-api work done; ii.patronId is: %s; ii.patronEmail is: %s' % (itemInstance.patronId, itemInstance.patronEmail), log_identifier, message_importance='low' )
    except Exception, e:
      updateLog( '- in utility_code.makeIlliadParametersV2(); patron-api work failed; exception is: %s' % e, log_identifier, message_importance='high' )
    parameter_dict = {
      'auth_key': settings.ILLIAD_API_KEY,
      'request_id': log_identifier,
      'first_name': itemInstance.firstname,  # used for new_user registration
      'last_name': itemInstance.lastname,  # used for new_user registration
      'username': itemInstance.eppn,  # for login _and_ new_user registration
      'address': '',  # used for new_user registration
      'email': itemInstance.patronEmail,  # used for new_user registration
      'oclc_number': itemInstance.oclcNumber,
      'openurl': makeOpenUrlSegment( itemInstance.sfxurl, log_identifier )['openurl_segment'],
      'patron_barcode': itemInstance.patronBarcode,
      'patron_department': itemInstance.patron_api_dept,  # used for new_user registration
      'patron_status': itemInstance.patronStatus,  # used for new_user registration
      'phone': '',  # used for new_user registration
      'volumes': '',  # perceived but not handled by dj_ill_submission
      }
    # updateLog( '- in utility_code.makeIlliadParametersV2(); parameter_dict: %s' % parameter_dict, log_identifier, message_importance='high' )  # TODO: lower hardcoded message_importance
    web_logger.post_message( message='- in utility_code.makeIlliadParametersV2()-wl; parameter_dict: %s' % unicode(repr(parameter_dict)), identifier=log_identifier, importance='info' )
    return { 'parameter_dict': parameter_dict }
  except:
    message = '- in utility_code.makeIlliadParametersV2(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { 'error_message': message }



def sendEmail( eb_request, log_identifier ):
  '''
  - Purpose: email director, hands off to more specific functions.
  - Called by: runCode()
  - Note: this will be built out to handle all emails.
  '''
  try:
    updateLog( '- in utility_code.sendEmail(); eb_request is: %s' % eb_request, log_identifier )
    if eb_request.request_current_tunneler_service == 'illiad':
      if eb_request.request_current_tunneler_status == 'login_failed_possibly_blocked':
        result_dict = sendEmailIlliadBlocked( eb_request, log_identifier )
    updateLog( '- in utility_code.sendEmail(); result_dict is: %s' % result_dict, log_identifier )
    return result_dict
  except:
    message = '- in utility_code.sendEmail(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { 'status': 'failure', 'message': message }
  # end def sendEmail()



def sendEmailActualSend( sender, recipient_list, full_message, log_identifier ):
  '''
  - Purpose: actually sends the email.
  - Called by: sendEmail() functions
  '''
  smtp_server = settings.MAIL_SMTP_SERVER
  smtp_result = 'init'
  updateLog( '- in uc.sendEmailActualSend(); starting send', log_identifier )
  try:
    mail_session = smtplib.SMTP( smtp_server )
    smtp_result = mail_session.sendmail( sender, recipient_list, full_message )
    updateLog( '- in uc.sendEmailActualSend(); email sent successfully; smtp_result is: %s' % smtp_result, log_identifier )
  except Exception, e:
    mail_session.quit()
    message = '- in uc.sendEmailActualSend(); attempt to send email failed; exception is: %s; smtp_result is: %s' % (e, smtp_result)
    updateLog( message, log_identifier, message_importance='high' )
    try:
      time.sleep(5) # 5 seconds of peace to recharge karma
      updateLog( '- second email attempt starting', log_identifier, message_importance='high' )
      mail_session_2 = smtplib.SMTP(smtp_server)
      smtp_result_2 = mail_session_2.sendmail(sender, recipient_list, full_message)
      updateLog( '- in uc.sendEmailActualSend(); second email sent successfully; smtp_result_2 is: %s' % smtp_result_2, log_identifier, message_importance='high' )
    except Exception, e:
      mail_session_2.quit()
      message = '- in uc.sendEmailActualSend(); second mail attempt failed; exception is: %s: smtp_result is: <<%s>>; and smtp_result_2 is: <<%s>>.' % (e, smtp_result, smtp_result_2)
      updateLog( message, log_identifier, message_importance='high' )
      return { 'status': 'failure', 'message': message }
    else:
      mail_session_2.quit()
      updateLog('- in uc.sendEmailActualSend(); mail_session2 quit normally; smtp_result_2 is: %s' % smtp_result_2, log_identifier )
      return { 'status': 'success' }
  else:
    mail_session.quit()
    updateLog('- in uc.sendEmailActualSend(); mail_session1 quit normally; smtp_result is: %s' % smtp_result, log_identifier )
    return { 'status': 'success' }
  # end def sendEmailActualSend()



def sendEmailIlliadBlocked( eb_request, log_identifier ):
  '''
  - Purpose: sends the 'illiad-blocked' email
  - Called by: uc.sendEmail()
  '''
  try:
    ## prep email
    sender = settings.MAIL_SENDER  # real account, not apparent to end-user
    recipient_list = eb_request.patron_email
    header_to = "To: %s" % eb_request.patron_email
    header_from = "From: %s" % settings.MAIL_APPARENT_SENDER
    header_reply_to = 'Reply-To: interlibrary_loan@brown.edu'
    header_subject = "Subject: Update on your 'easyBorrow' request -- *problem*"
    header_info = header_to + "\n" + header_from + "\n" + header_reply_to + "\n" + header_subject
    message = '''
Greetings %s %s,

Your request for the item, '%s', could not be fulfilled by our easyBorrow service. It appears there is a problem with your Interlibrary Loan, ILLiad account.

Contact the Interlibrary Loan office at the email address above or at 401/863-2169. The staff will work with you to resolve the problem.

Once your account issue is cleared up, click on this link to re-request the item:
<%s>

( easyBorrow request reference number: '%s' )

[end]
    ''' % (
    eb_request.patron_firstname,
    eb_request.patron_lastname,
    eb_request.item_title,
    'http://worldcat.org/oclc/%s' % eb_request.item_oclc_number,
    eb_request.request_ezb_reference_number,
    )
    full_message = header_info + "\n" + message
    updateLog( '- in utility_code.sendEmailIlliadBlocked(); sender: %s; recipient_list: %s; full_message: %s' % (sender, recipient_list, full_message), log_identifier )
    ## send the email
    send_result = sendEmailActualSend( sender, recipient_list, full_message, log_identifier )
    if send_result['status'] == 'success':
      return_dict = { 'status': 'success' }
    else:
      return_dict = { 'status': 'failure', 'message': send_result }
    updateLog( '- in utility_code.sendEmailIlliadBlocked(); return_dict: %s' % return_dict, log_identifier )
    return return_dict
  except:
    message = '- in utility_code.sendEmailIlliadBlocked(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { 'status': 'failure', 'message': message }
  # end def sendEmailIlliadBlocked()



def submitIlliadRequest( parameter_dict, log_identifier ):
  '''
  - Purpose: hits the django illiad submission web-service.
  - Called by: controller.runCode()
  - Usage: see tests.doc_tests.test_submitIlliadRequest()
  '''

  try:

    updateLog( '- in utility_code.submitIlliadRequest(); parameter_dict is: %s' % parameter_dict, log_identifier, message_importance='high' )

    data = urllib.urlencode( parameter_dict )
    request = urllib2.Request( settings.ILLIAD_REQUEST_URL, data )
    response = urllib2.urlopen( request )
    json_string = response.read()
    json_dict = json.loads( json_string )
    updateLog( '- in utility_code.submitIlliadRequest(); submission result is: %s' % json_dict, log_identifier, message_importance='high' )

    return json_dict

  except:
    message = '- in utility_code.submitIlliadRequest(); error detail: %s' % makeErrorString()
    # updateLog( message, log_identifier, message_importance='high' )
    return { 'status': 'failure', 'message': message }

  # end def submitIlliadRequest()



def submitIlliadRemoteAuthRequestV2( parameter_dict, log_identifier ):
  try:
    url = settings.ILLIAD_API_URL
    headers = { 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8' }
    r = requests.post( url, data=parameter_dict, headers=headers, timeout=60, verify=False )
    updateLog( '- in utility_code.submitIlliadRequestV2(); ws response text: %s' % r.text, log_identifier )
    return_dict = json.loads( r.text )
    updateLog( '- in utility_code.submitIlliadRequestV2(); return_dict: %s' % return_dict, log_identifier, message_importance='high' )  # TODO: remove hardcoded importance
    return return_dict
  except:
    message = '- in utility_code.submitIlliadRequestV2(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { 'error_message': message }
  # end def submitIlliadRemoteAuthRequestV2()



def updateLog( message, log_identifier, message_importance='low' ):

  try:

    update_log_flag = 'init'

    if message_importance == 'high':
      update_log_flag = 'yes'
    elif (message_importance == 'low' and settings.LOGENTRY_MINIMUM_IMPORTANCE_LEVEL == 'low' ):
      update_log_flag = 'yes'
    else:
      pass # there definitely are many other conditions that will get us here -- but the whole point is not to log everything.

    if update_log_flag == 'yes':
      values = { 'message': message, 'identifier': log_identifier, 'key': settings.LOG_KEY }
      data = urllib.urlencode( values )
      request = urllib2.Request( settings.LOG_URL, data )
      response = urllib2.urlopen( request, timeout=3 )
      returned_data = response.read()
      return returned_data

  except:
    print '- in utility_code.updateLog(); error detail: %s' % makeErrorString()

  # end def updateLog()



def jsonify_db_data( data_dict ):
  """ Returns json string for given tuple of row-dict entries.
      Allows result to be logged easily.
      Called by ezb_controller.py """
  data_dict['created'] = unicode( data_dict['created'] )
  jstring = json.dumps( data_dict, sort_keys=True, indent=2 )
  return jstring
