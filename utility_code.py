# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, json, logging, os, pprint, smtplib, sys, time, urllib, urllib2
import requests
from easyborrow_controller_code import settings
from easyborrow_controller_code.classes.web_logger import WebLogger


## file and web-loggers
LOG_PATH = settings.LOG_PATH
LOG_LEVEL = settings.LOG_LEVEL
level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
logger = logging.getLogger(__name__)
web_logger = WebLogger( logger )


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
        web_logger.post_message( message='- in utility_code.evaluateIlliadSubmissionV2(); Illiad user created...', identifier=log_identifier, importance='info' )
        parameterDict = { 'serviceName': 'illiad', 'action': 'create_illiad_user_attempt', 'result': 'success', 'number': '' }
        # itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )
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
        # patronInfo = itemInstance.grabPatronApiInfo(itemInstance.patronId)
        # itemInstance.grabConvertedPatronApiInfo(patronInfo) # grabs converted info and stores it to attributes
      if parameterDict == None:
        parameterDict = { 'serviceName': 'illiad', 'action': 'attempt', 'result': send_result_dict['status'], 'number': '' }
      # itemInstance.updateHistoryAction( parameterDict['serviceName'], parameterDict['action'], parameterDict['result'], parameterDict['number'] )
      return_dict['status'] = 'evaluation_successful'
    web_logger.post_message( message='- in utility_code.evaluateIlliadSubmissionV2(); return_dict: %s' % unicode(repr(return_dict)), identifier=log_identifier, importance='info' )
    return return_dict
  except:
    message = '- in utility_code.evaluateIlliadSubmissionV2(); error detail: %s' % makeErrorString()
    web_logger.post_message( message=message, identifier=log_identifier, importance='info' )
    return { 'error_message': message }



def jsonify(structure, rq_indent=2):
  '''
  - Purpose: serializes and formats non-model object in json.
  - Called by: multiple functions.
  '''
  data = json.dumps( structure, sort_keys=True, indent=rq_indent )
  return data
  # end def jsonify()



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
    logger.debug( 'id, `%s`; eb_request.__dict__ is: %s' % (log_identifier, eb_request.__dict__) )
    return_dict = { 'status': 'success', 'eb_request': eb_request }
    logger.debug( 'id, `%s`; return_dict is: %s' % (log_identifier, pprint.pformat(return_dict)) )
    return return_dict
  except:
    message = '- in utility_code.makeEbRequest(); error detail: %s' % makeErrorString()
    web_logger.post_message( message='- in utility_code.makeEbRequest(); exception, `%s`' % message, identifier=log_identifier, importance='error' )
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



def sendEmail( eb_request, log_identifier ):
  '''
  - Purpose: email director, hands off to more specific functions.
  - Called by: runCode()
  - Note: this will be built out to handle all emails.
  '''
  try:
    logger.debug( 'id, `%s`; eb_request is: %s' % (log_identifier, unicode(repr(eb_request))) )
    if eb_request.request_current_tunneler_service == 'illiad':
      if eb_request.request_current_tunneler_status == 'login_failed_possibly_blocked':
        result_dict = sendEmailIlliadBlocked( eb_request, log_identifier )
    logger.debug( 'id, `%s`; result_dict is, ```%s```' % (log_identifier, pprint.pformat(result_dict)) )
    return result_dict
  except:
    message = '- in utility_code.sendEmail(); error detail: %s' % makeErrorString()
    web_logger.post_message( message=message, identifier=log_identifier, importance='error' )
    return { 'status': 'failure', 'message': message }
  # end def sendEmail()



def sendEmailActualSend( sender, recipient_list, full_message, log_identifier ):
  '''
  - Purpose: actually sends the email.
  - Called by: sendEmail() functions
  '''
  smtp_server = settings.MAIL_SMTP_SERVER
  smtp_result = 'init'
  logger.debug( 'id, `%s`; starting send' % log_identifier )
  try:
    mail_session = smtplib.SMTP( smtp_server )
    smtp_result = mail_session.sendmail( sender, recipient_list, full_message )
    logger.debug( 'id, `%s`; email sent successfully; smtp_result is: ```%s```' % (log_identifier, unicode(repr(smtp_result))) )
  except Exception, e:
    mail_session.quit()
    message = '- in uc.sendEmailActualSend(); attempt to send email failed; exception is: %s; smtp_result is: %s' % ( unicode(repr(e)), unicode(repr(smtp_result)) )
    web_logger.post_message( message=message, identifier=log_identifier, importance='error' )
    try:
      time.sleep(5) # 5 seconds of peace to recharge karma
      web_logger.post_message( message='- in uc.sendEmailActualSend(); second email attempt starting', identifier=log_identifier, importance='info' )
      mail_session_2 = smtplib.SMTP(smtp_server)
      smtp_result_2 = mail_session_2.sendmail(sender, recipient_list, full_message)
      web_logger.post_message( message='- in uc.sendEmailActualSend(); second email sent successfully; smtp_result_2 is: %s' % unicode(repr(smtp_result_2)), identifier=log_identifier, importance='info' )
    except Exception, e:
      mail_session_2.quit()
      message = '- in uc.sendEmailActualSend(); second mail attempt failed; exception is: %s: smtp_result is: <<%s>>; and smtp_result_2 is: <<%s>>.' % ( unicode(repr(e)), unicode(repr(smtp_result)), unicode(repr(smtp_result_2)) )
      web_logger.post_message( message=message, identifier=log_identifier, importance='error' )
      return { 'status': 'failure', 'message': message }
    else:
      mail_session_2.quit()
      logger.debug( 'id, `%s`; mail_session2 quit normally; smtp_result_2 is: `%s`' % (log_identifier, unicode(repr(smtp_result_2))) )
      return { 'status': 'success' }
  else:
    mail_session.quit()
    logger.debug( 'id, `%s`; mail_session1 quit normally; smtp_result is: %s' % (log_identifier, unicode(repr(smtp_result))) )
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
    logger.debug( 'id, `%s`; sender: %s; recipient_list: %s; full_message: %s' % (log_identifier, unicode(repr(sender)), unicode(repr(recipient_list)), unicode(repr(full_message)) ) )
    ## send the email
    send_result = sendEmailActualSend( sender, recipient_list, full_message, log_identifier )
    if send_result['status'] == 'success':
      return_dict = { 'status': 'success' }
    else:
      return_dict = { 'status': 'failure', 'message': send_result }
    logger.debug( 'id, `%s`; return_dict: %s' % (log_identifier, pprint.pformat(return_dict)) )
    return return_dict
  except:
    message = '- in utility_code.sendEmailIlliadBlocked(); error detail: %s' % makeErrorString()
    web_logger.post_message( message=message, identifier=log_identifier, importance='error' )
    return { 'status': 'failure', 'message': message }
  # end def sendEmailIlliadBlocked()



# def submitIlliadRequest( parameter_dict, log_identifier ):
#   '''
#   - Purpose: hits the django illiad submission web-service.
#   - Called by: controller.runCode()
#   - Usage: see tests.doc_tests.test_submitIlliadRequest()
#   '''

#   try:

#     web_logger.post_message( message='- in utility_code.submitIlliadRequest(); parameter_dict is: %s' % pprint.pformat(parameter_dict), identifier=log_identifier, importance='info' )

#     data = urllib.urlencode( parameter_dict )
#     request = urllib2.Request( settings.ILLIAD_REQUEST_URL, data )
#     response = urllib2.urlopen( request )
#     json_string = response.read()
#     json_dict = json.loads( json_string )
#     web_logger.post_message( message='- in utility_code.submitIlliadRequest(); submission result is: %s' % pprint.pformat(json_dict), identifier=log_identifier, importance='info' )
#     return json_dict

#   except:
#     message = '- in utility_code.submitIlliadRequest(); error detail: %s' % makeErrorString()
#     web_logger.post_message( message=message, identifier=log_identifier, importance='error' )
#     return { 'status': 'failure', 'message': message }

#   # end def submitIlliadRequest()



# def submitIlliadRemoteAuthRequestV2( parameter_dict, log_identifier ):
#   try:
#     url = settings.ILLIAD_API_URL
#     headers = { 'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8' }
#     r = requests.post( url, data=parameter_dict, headers=headers, timeout=60, verify=False )
#     logger.debug( 'id, `%s`; ws response text, ```%s```' % (log_identifier, r.text) )
#     return_dict = json.loads( r.text )
#     web_logger.post_message( message='- in utility_code.submitIlliadRequestV2(); return_dict: %s' % pprint.pformat(return_dict), identifier=log_identifier, importance='info' )
#     return return_dict
#   except:
#     message = '- in utility_code.submitIlliadRequestV2(); error detail: %s' % makeErrorString()
#     web_logger.post_message( message=message, identifier=log_identifier, importance='error' )
#     return { 'error_message': message }
#   # end def submitIlliadRemoteAuthRequestV2()



# def jsonify_db_data( data_dict ):
#   """ Returns json string for given tuple of row-dict entries.
#       Allows result to be logged easily.
#       Called by ezb_controller.py """
#   data_dict['created'] = unicode( data_dict['created'] )
#   jstring = json.dumps( data_dict, sort_keys=True, indent=2 )
#   return jstring
