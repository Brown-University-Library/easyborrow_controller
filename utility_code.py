# -*- coding: utf-8 -*-

import datetime, json, os, pprint, sys
import requests
# from easyborrow_project_local_settings import ezb_controller_local_settings as ezb_settings  # new style
from easyborrow_controller_code import settings


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



def createIlliadUser( eb_request, log_identifier ):
  '''
  - Purpose: prepare request, submit it, and return result to controller.
  - Called by: controller().
  '''

  try:
    import urllib, urllib2

    # prepare parameters
    parameter_dict = {
      'easyborrow_key': log_identifier,
      'firstname': eb_request.patron_firstname,
      'lastname': eb_request.patron_lastname,
      'email': eb_request.patron_email,
      'phone': eb_request.patron_phone,
      'address': eb_request.patron_address,
      'patron_status': eb_request.patron_status,
      'department': eb_request.patron_department }
    updateLog( '- in controller.uc.createIlliadUser(); parameter_dict is: %s' % parameter_dict, log_identifier )

    # submit post
    post_data = urllib.urlencode( parameter_dict )
    request = urllib2.Request( settings.ILLIAD_NEWUSER_WEBSERVICE_URL, post_data )
    response = urllib2.urlopen( request )
    json_string = response.read()
    updateLog( '- in controller.uc.createIlliadUser(); json_string is: %s' % json_string, log_identifier )

    # analyze result
    json_dict = json.loads( json_string )
    if json_dict['status'] == 'success':
      return { u'status': u'success' }
    else:
      return { u'status': u'failure', u'message': json_string }

  except:  # reasonable on a 403/Forbidden
    message = u'- in controller.uc.createIlliadUser(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { u'status': u'failure', u'message': message }

  # end def createIlliadUser()



def evaluateIlliadSubmissionV2( itemInstance, send_result_dict, log_identifier ):
  try:
    return_dict = { u'status': u'init' }
    ## new-user check
    if u'new_user' in send_result_dict:
      if send_result_dict[u'new_user'] == True:
        updateLog( u'- in controller.uc.evaluateIlliadSubmissionV2(); Illiad user created...', log_identifier, message_importance='high' )
        parameterDict = { u'serviceName': u'illiad', u'action': u'create_illiad_user_attempt', u'result': u'success', u'number': u'' }
        itemInstance.updateHistoryAction( parameterDict[u'serviceName'], parameterDict[u'action'], parameterDict[u'result'], parameterDict[u'number'] )
    ## illiad status check
    if u'status' in send_result_dict:
      parameterDict = None  # for history update
      if send_result_dict[u'status'] == u'submission_successful':
        itemInstance.illiadAssignedReferenceNumber = send_result_dict[u'transaction_number']  # it should be there
        parameterDict = { u'serviceName': u'illiad', u'action': u'attempt', u'result': u'Request_Successful', u'number': itemInstance.illiadAssignedReferenceNumber }
        itemInstance.requestSuccessStatus = u'success'
        itemInstance.genericAssignedUserEmail = itemInstance.patronEmail
        itemInstance.genericAssignedReferenceNumber = itemInstance.illiadAssignedReferenceNumber
      elif send_result_dict[u'status'] == u'login_failed_possibly_blocked':
        itemInstance.requestSuccessStatus = u'login_failed_possibly_blocked'
        itemInstance.genericAssignedUserEmail = itemInstance.patronEmail
        patronInfo = itemInstance.grabPatronApiInfo(itemInstance.patronId)
        itemInstance.grabConvertedPatronApiInfo(patronInfo) # grabs converted info and stores it to attributes
      if parameterDict == None:
        parameterDict = { u'serviceName': u'illiad', u'action': u'attempt', u'result': send_result_dict[u'status'], u'number': u'' }
      itemInstance.updateHistoryAction( parameterDict[u'serviceName'], parameterDict[u'action'], parameterDict[u'result'], parameterDict[u'number'] )
      return_dict[u'status'] = u'evaluation_successful'
    updateLog( u'- in controller.uc.evaluateIlliadSubmissionV2(); return_dict: %s' % return_dict, log_identifier, message_importance='high' )
    return return_dict
  except:
    message = u'- in controller.uc.evaluateIlliadSubmissionV2(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { u'error_message': message }



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
    updateLog( u'- in controller.uc.makeOpenUrlSegment(); initial_url is: %s' % initial_url, log_identifier )
    parsed_url = initial_url[ initial_url.find( u'serialssolutions.com/?' ) + 22 : ]  # TODO: change this to use the urlparse library
    # parsed_url = initial_url[ initial_url.find( 'sid' ) : ]
    parsed_url = parsed_url.replace( u'genre=unknown', u'genre=book' )
    updateLog( u'- in controller.uc.makeOpenUrlSegment(); parsed_url is: %s' % parsed_url, log_identifier )
    return { u'openurl_segment': parsed_url }
  except:
    message = u'- in controller.uc.updateLog(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance=u'high' )
    return { u'status': u'failure', u'message': message }



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
    updateLog( u'- in controller.uc.makeEbRequest(); eb_request.__dict__ is: %s' % eb_request.__dict__, log_identifier )
    return_dict = { u'status': u'success', u'eb_request': eb_request }
    updateLog( u'- in controller.uc.makeEbRequest(); return_dict is: %s' % return_dict, log_identifier )
    return return_dict
  except:
    message = u'- in controller.uc.updateLog(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { u'status': u'failure', u'message': message }
  # end def makeEbRequest()



def makeErrorString():
  '''
  - Purpose: to return detailed error information for logging/debugging.
  - Called by: could be any exception block.
  '''

  import sys
  return u'error-type - %s; error-message - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, )

  # end def makeErrorString()



def makeIdentifier():
  '''
  - Purpose: temp identifier for logging, until request number is availablet.
  - Called by controller()
  '''

  import datetime, random
  identifier = 'temp--%s--%s' % ( datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), random.randint(1000,9999) )
  return identifier



def make_datetime_string():
  """ Returns time-string like 'Wed Oct 23 14:49:38 EDT 2013'. """
  import time
  time_object = time.localtime(); assert type(time_object) == time.struct_time
  time_string = time.strftime( u'%a %b %d %H:%M:%S %Z %Y', time_object )
  return time_string



def makeIlliadParametersV2( itemInstance, settings, log_identifier ):
  try:
    updateLog( u'- in controller.uc.makeIlliadParametersV2(); starting...', log_identifier, message_importance='high' )  # TODO: lower hardcoded message_importance
    try:
      patron_info = itemInstance.grabPatronApiInfo( itemInstance.patronId )
      itemInstance.grabConvertedPatronApiInfo( patron_info) # grabs converted info and stores it to attributes
      updateLog( u'- in controller.uc.makeIlliadParametersV2(); patron-api work done; ii.patronId is: %s; ii.patronEmail is: %s' % (itemInstance.patronId, itemInstance.patronEmail), log_identifier, message_importance='low' )
    except Exception, e:
      updateLog( u'- in controller.uc.makeIlliadParametersV2(); patron-api work failed; exception is: %s' % e, log_identifier, message_importance='high' )
    parameter_dict = {
      u'auth_key': settings.ILLIAD_REMOTEAUTH_KEY,
      u'request_id': log_identifier,
      u'first_name': itemInstance.firstname,  # used for new_user registration
      u'last_name': itemInstance.lastname,  # used for new_user registration
      u'username': itemInstance.eppn,  # for login _and_ new_user registration
      u'address': '',  # used for new_user registration
      u'email': itemInstance.patronEmail,  # used for new_user registration
      u'oclc_number': itemInstance.oclcNumber,
      u'openurl': makeOpenUrlSegment( itemInstance.sfxurl, log_identifier )['openurl_segment'],
      u'patron_barcode': itemInstance.patronBarcode,
      u'patron_department': itemInstance.patron_api_dept,  # used for new_user registration
      u'patron_status': itemInstance.patronStatus,  # used for new_user registration
      u'phone': '',  # used for new_user registration
      u'volumes': '',  # perceived but not handled by dj_ill_submission
      }
    updateLog( u'- in controller.uc.makeIlliadParametersV2(); parameter_dict: %s' % parameter_dict, log_identifier, message_importance='high' )  # TODO: lower hardcoded message_importance
    return { u'parameter_dict': parameter_dict }
  except:
    message = u'- in controller.uc.makeIlliadParametersV2(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { u'error_message': message }



def sendEmail( eb_request, log_identifier ):
  '''
  - Purpose: email director, hands off to more specific functions.
  - Called by: runCode()
  - Note: this will be built out to handle all emails.
  '''
  try:
    updateLog( '- in controller.uc.sendEmail(); eb_request is: %s' % eb_request, log_identifier )
    if eb_request.request_current_tunneler_service == 'illiad':
      if eb_request.request_current_tunneler_status == 'login_failed_possibly_blocked':
        result_dict = sendEmailIlliadBlocked( eb_request, log_identifier )
    updateLog( '- in controller.uc.sendEmail(); result_dict is: %s' % result_dict, log_identifier )
    return result_dict
  except:
    message = u'- in controller.uc.sendEmail(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { u'status': u'failure', u'message': message }
  # end def sendEmail()



def sendEmailActualSend( sender, recipient_list, full_message, log_identifier ):
  '''
  - Purpose: actually sends the email.
  - Called by: sendEmail() functions
  '''
  import smtplib
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
    updateLog( '- in controller.uc.sendEmailIlliadBlocked(); sender: %s; recipient_list: %s; full_message: %s' % (sender, recipient_list, full_message), log_identifier )
    ## send the email
    send_result = sendEmailActualSend( sender, recipient_list, full_message, log_identifier )
    if send_result['status'] == 'success':
      return_dict = { 'status': 'success' }
    else:
      return_dict = { 'status': 'failure', 'message': send_result }
    updateLog( '- in controller.uc.sendEmailIlliadBlocked(); return_dict: %s' % return_dict, log_identifier )
    return return_dict
  except:
    message = u'- in controller.uc.sendEmailIlliadBlocked(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance='high' )
    return { u'status': u'failure', u'message': message }
  # end def sendEmailIlliadBlocked()



def submitIlliadRequest( parameter_dict, log_identifier ):
  '''
  - Purpose: hits the django illiad submission web-service.
  - Called by: controller.runCode()
  - Usage: see tests.doc_tests.test_submitIlliadRequest()
  '''

  try:

    from easyborrow_controller_code import settings
    import json, urllib, urllib2

    updateLog( u'- in controller.uc.submitIlliadRequest(); parameter_dict is: %s' % parameter_dict, log_identifier, message_importance='high' )

    data = urllib.urlencode( parameter_dict )
    request = urllib2.Request( settings.ILLIAD_REQUEST_URL, data )
    response = urllib2.urlopen( request )
    json_string = response.read()
    json_dict = json.loads( json_string )
    updateLog( u'- in controller.uc.submitIlliadRequest(); submission result is: %s' % json_dict, log_identifier, message_importance='high' )

    return json_dict

  except:
    message = u'- in controller.uc.submitIlliadRequest(); error detail: %s' % makeErrorString()
    # updateLog( message, log_identifier, message_importance='high' )
    return { u'status': u'failure', u'message': message }

  # end def submitIlliadRequest()



def submitIlliadRemoteAuthRequestV2( parameter_dict, log_identifier ):
  try:
    import json, pprint
    import requests
    url = u'%s://127.0.0.1/easyborrow/ill/v2/make_request/' % settings.ILLIAD_HTTP_S_SEGMENT
    headers = { u'Content-Type': u'application/x-www-form-urlencoded; charset=utf-8' }
    r = requests.post( url, data=parameter_dict, headers=headers, timeout=60, verify=False )
    updateLog( u'- in controller.uc.submitIlliadRequestV2(); ws response text: %s' % r.text, log_identifier )
    return_dict = json.loads( r.text )
    updateLog( u'- in controller.uc.submitIlliadRequestV2(); return_dict: %s' % return_dict, log_identifier, message_importance=u'high' )  # TODO: remove hardcoded importance
    return return_dict
  except:
    message = u'- in controller.uc.submitIlliadRequestV2(); error detail: %s' % makeErrorString()
    updateLog( message, log_identifier, message_importance=u'high' )
    return { u'error_message': message }
  # end def submitIlliadRemoteAuthRequestV2()



def updateLog( message, log_identifier, message_importance='low' ):

  try:

    from easyborrow_controller_code import settings
    import urllib, urllib2

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
    print u'- in controller.uc.updateLog(); error detail: %s' % makeErrorString()

  # end def updateLog()



def jsonify_db_data( data_dict ):
  """ Returns json string for given tuple of row-dict entries.
      Allows result to be logged easily.
      Called by ezb_controller.py """
  data_dict[u'created'] = unicode( data_dict[u'created'] )
  jstring = json.dumps( data_dict, sort_keys=True, indent=2 )
  return jstring



class DB_Logger(object):
  """ Manages databaselogging.
      All database log entries, as well as failure attempts, also populate a file-log.
      self.session_identifier is populated early, and logger instance is passed to other classes. """

  def __init__( self, file_logger, LOG_URL, LOG_KEY, LOGENTRY_MINIMUM_IMPORTANCE_LEVEL ):
    """ Holds a bit of state. """
    self.file_logger = file_logger
    self.LOG_URL = LOG_URL
    self.LOG_KEY = LOG_KEY
    self.LOGENTRY_MINIMUM_IMPORTANCE_LEVEL = LOGENTRY_MINIMUM_IMPORTANCE_LEVEL
    self.session_identifier = makeIdentifier()  # used until request-number is obtained

  def update_log( self, message, message_importance=u'low' ):
    """ Updates database log. And file log. """
    try:
      assert message_importance in [u'low', u'high']
      update_log_flag = False
      if message_importance == u'high':
        update_log_flag = True
      elif ( message_importance == u'low' and self.LOGENTRY_MINIMUM_IMPORTANCE_LEVEL == u'low' ):
        update_log_flag = True
      if update_log_flag:
        values = { u'message': message, u'identifier': self.session_identifier, u'key': self.LOG_KEY }
        r = requests.post( self.LOG_URL, data=values, verify=False )
      self.file_logger.info( u'session, %s; message, %s' % (self.session_identifier, message) )
      return
    except:
      message = u'- in uc.DB_Logger.update_log(); error detail: %s' % makeErrorString()
      print message
      self.file_logger.error( u'session, %s; message, %s' % (self.session_identifier, message) )
      return

  # end class DB_Logger()



class DB_Handler(object):

  def __init__(self, db_host, db_port, db_username, db_password, db_name, db_logger ):
    """ Sets up basics. """
    self.db_host = db_host
    self.db_port = db_port
    self.db_username = db_username
    self.db_password = db_password
    self.db_name = db_name
    self.connection_object = None  # populated during queries
    self.cursor_object = None  # populated during queries
    self.db_logger = db_logger

  def execute_sql(self, sql):
    """ Executes sql; returns tuple of row-dicts.
        Example return data: ( {row1field1key: row1field1value, row1field2key: row1field2value}, {row2field1key: row2field1value, row2field2key: row2field2value} )
        Called by Controller.get_new_data(), self.update_request_status() """
    try:
      self._setup_db_connection()
      if not self.cursor_object:
        return
      self.cursor_object.execute( sql )
      dict_list = self.cursor_object.fetchall()  # really a tuple of row-dicts

      self.db_logger.update_log( message=u'- in dev_ezb_controller.py; uc.DB_Handler.execute_sql(); dict_list: %s' % dict_list, message_importance='low' )
      dict_list = self._unicodify_resultset( dict_list )
      self.db_logger.update_log( message=u'- in dev_ezb_controller.py; uc.DB_Handler.execute_sql(); dict_list NOW: %s' % dict_list, message_importance='low' )

      return dict_list
    except Exception as e:
      message = u'- in dev_ezb_controller.py; uc.DB_Handler.execute_sql(); error: %s' % unicode( repr(e).decode(u'utf8', u'replace') )
      self.db_logger.update_log( message=message, message_importance='high' )
      return None
    finally:
      self._close_db_connection()

  def _setup_db_connection( self ):
    """ Sets up connection; populates instance attributes.
        Called by run_select() """
    try:
      import MySQLdb
      self.connection_object = MySQLdb.connect(
        host=self.db_host, port=self.db_port, user=self.db_username, passwd=self.db_password, db=self.db_name )
      self.cursor_object = self.connection_object.cursor(MySQLdb.cursors.DictCursor)
      return
    except Exception as e:
      message = u'- in dev_ezb_controller.py; uc.DB_Handler._setup_db_connection(); error: %s' % unicode( repr(e).decode(u'utf8', u'replace') )
      self.db_logger.update_log( message=message, message_importance='high' )

  def _unicodify_resultset( self, dict_list ):
    """ Returns dict with keys and values as unicode-strings. """
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
      message = u'- in dev_ezb_controller.py; uc.DB_Handler._unicodify_resultset(); error: %s' % unicode( repr(e).decode(u'utf8', u'replace') )
      self.db_logger.update_log( message=message, message_importance='high' )

  def _close_db_connection( self ):
    """ Closes db connection.
        Called by run_select() """
    try:
      self.cursor_object.close()
      self.connection_object.close()
      message = u'- in dev_ezb_controller.py; uc.DB_Handler._close_db_connection(); db connection closed'
      self.db_logger.update_log( message=message, message_importance='low' )
      return
    except Exception as e:
      message = u'- in dev_ezb_controller.py; uc.DB_Handler._close_db_connection(); error: %s' % unicode( repr(e).decode(u'utf8', u'replace') )
      self.db_logger.update_log( message=message, message_importance='high' )

  def update_request_status( self, row_id, status ):
    """ Updates request table status field.
        Called by ezb_controller.py """
    SQL_PATTERN = unicode( os.environ[u'ezbCTL__UPDATE_REQUEST_STATUS_SQL_PATTERN'] )
    sql = SQL_PATTERN % ( status, row_id )
    result = self.execute_sql( sql )
    self.db_logger.update_log(
      message=u'- in dev_ezb_controller.py; uc.DB_Handler.update_request_status(); status updated to %s' % status, message_importance=u'low' )
    return

  def update_history_note( self, request_id, note ):
    """ Updates history table note field.
        Called by ezb_controller.py """

    SQL_PATTERN = unicode( os.environ[u'ezbCTL__INSERT_HISTORY_NOTE_SQL_PATTERN'] )
    sql = SQL_PATTERN % ( request_id, note )

    result = self.execute_sql( sql )
    self.db_logger.update_log(
      message=u'- in dev_ezb_controller.py; uc.DB_Handler.update_history_note(); note updated', message_importance=u'low' )
    return

  # end class DB_Handler()
