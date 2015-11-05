# -*- coding: utf-8 -*-

import os, sys
from easyborrow_controller_code import settings


class UtilityCode( object ):


  def __init__( self, logger ):
    self.timeToFormat = ""
    self.log = ""
    self.log_identifier = u''  # set by controller.run_code()
    self.logger = logger  # set by Controller() or Item()


  def updateLog( self, message, message_importance, identifier='' ):
    """ Older web-db logging code. TODO: replace with classes.weblogger.WebLogger() calls. """
    try:
      import urllib, urllib2
      update_log_flag = 'init'
      if message_importance == 'high':
        update_log_flag = 'yes'
      elif (message_importance == 'low' and settings.OLD_WEBLOG_LEVEL == 'low' ):
        update_log_flag = 'yes'
      else:
        pass # there definitely are many other conditions that will get us here -- but the whole point is not to log everything.
      if update_log_flag == 'yes':
        values = { 'message':message, 'identifier':identifier, 'key':settings.LOG_KEY }
        data = urllib.urlencode(values)
        request = urllib2.Request(settings.LOG_URL, data)
        response = urllib2.urlopen(request)
        returned_data = response.read()
        return returned_data
    except Exception, e:
      print '- in UC.updateLog; exception is: %s' % repr(e)
    # end def updateLog()


  def connectExecute(self, sql):
    """ Older db-access code. TODO: replace with classes.db_handler.Db_Handler() calls. """
    try:
      # I think this environ thing doesn't really work; that I fixed it externally.
      import os
      os.environ["LD_LIBRARY_PATH"] = unicode( os.environ[u'ezbCTL__MYSQL_DIRECTORY_PATH'] )
      import MySQLdb
      DB_NAME = unicode( os.environ[u'ezbCTL__DB_NAME'] )
      try:
        connectionObject = MySQLdb.connect(host=settings.DB_HOST, port=settings.DB_PORT, user=settings.DB_USERNAME, passwd=settings.DB_PASSWORD, db=DB_NAME)
        cursorObject = connectionObject.cursor()
        cursorObject.execute(sql)
        recordId = int( cursorObject.insert_id() )
        cursorObject.close()
        connectionObject.close()
        returnVal = recordId  # 2012-10-04: this doesn't seem to work, thus always generating a returnVal of 'failure', which doesn't matter since it's not used.
      except Exception, e:
        returnVal = "failure"
      return returnVal
    except Exception, e:
      self.updateLog( message=u'- in controller.uc.connectExecute(); exception is: %s' % repr(e).decode(u'utf-8', u'replace'), message_importance=u'high', identifier=u'unavailable' )
    # end def connectExecute()


  # def connectExecute(self, sql):

  #   try:

  #     # I think this environ thing doesn't really work; that I fixed it externally.
  #     import os
  #     os.environ["LD_LIBRARY_PATH"] = unicode( os.environ[u'ezbCTL__MYSQL_DIRECTORY_PATH'] )

  #     import MySQLdb
  #     import Prefs
  #     prefsInstance = Prefs.Prefs()
  #     DB_NAME = unicode( os.environ[u'ezbCTL__DB_NAME'] )

  #     try:
  #       connectionObject = MySQLdb.connect(host=prefsInstance.db_host, port=prefsInstance.db_port, user=prefsInstance.db_username, passwd=prefsInstance.db_password, db=DB_NAME)
  #       cursorObject = connectionObject.cursor()

  #       cursorObject.execute(sql)
  #       recordId = int( cursorObject.insert_id() )

  #       cursorObject.close()
  #       connectionObject.close()

  #       returnVal = recordId  # 2012-10-04: this doesn't seem to work, thus always generating a returnVal of 'failure', which doesn't matter since it's not used.

  #     except Exception, e:
  #       returnVal = "failure"

  #     return returnVal

  #   except Exception, e:
  #     self.updateLog( message=u'- in controller.uc.connectExecute(); exception is: %s' % repr(e).decode(u'utf-8', u'replace'), message_importance=u'high', identifier=u'unavailable' )



  def connectExecuteSelect(self, sql):

    import os
    import MySQLdb
    import Prefs

    prefsInstance = Prefs.Prefs()
    DB_NAME = unicode( os.environ[u'ezbCTL__DB_NAME'] )

    connectionObject = MySQLdb.connect(host=prefsInstance.db_host, port=prefsInstance.db_port, user=prefsInstance.db_username, passwd=prefsInstance.db_password, db=DB_NAME)
    cursorObject = connectionObject.cursor()
    cursorObject.execute(sql)

    dataTuple = cursorObject.fetchall()
    fields = cursorObject.description

    if( dataTuple == () ):
      return None

    else:
      fieldList = []
      for elementInfo in fields:
        fieldList.append(elementInfo[0])

    resultInfo = [fieldList, dataTuple] # [ [fieldname01, fieldname02], ( (row01field01_value, row01field02_value), (row02field01_value, row02field02_value) ) ]

    cursorObject.close()
    connectionObject.close()

    return resultInfo



  def prepFirstEmailHeader( self, itemInstance ):
    '''
    - Called by: UtilityCode.py->UtilityCode.sendEmail()
    - Purpose: Prepare header info for main email.
    '''
    ADMIN_EMAIL = unicode( os.environ[u'ezbCTL__ADMIN_EMAIL'] )
    CIRC_ADMIN_EMAIL = unicode( os.environ[u'ezbCTL__CIRC_ADMIN_EMAIL'] )

    if ( itemInstance.currentlyActiveService == 'inRhode' and itemInstance.requestSuccessStatus == 'success' ):
      headerTo = "To: %s" % (itemInstance.patronEmail)
      headerFrom = "From: brown_library_easyborrow_system"
      headerReplyTo = 'Reply-To: rock@brown.edu'
      headerSubject = "Subject: Update on your 'easyBorrow' request"
    elif( itemInstance.currentlyActiveService == 'borrowDirect' and itemInstance.requestSuccessStatus == 'success' ):
      headerTo = "To: %s" % (itemInstance.patronEmail)
      headerFrom = "From: brown_library_easyborrow_system"
      headerReplyTo = 'Reply-To: rock@brown.edu'
      headerSubject = "Subject: Update on your 'easyBorrow' request"
    elif( itemInstance.currentlyActiveService == 'virtualCatalog' and itemInstance.requestSuccessStatus == 'success' ):
      headerTo = "To: %s" % (itemInstance.patronEmail)
      headerFrom = "From: brown_library_easyborrow_system"
      headerReplyTo = 'Reply-To: rock@brown.edu'
      headerSubject = "Subject: Update on your 'easyBorrow' request"
    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'success' ):
      headerTo = "To: %s" % (itemInstance.patronEmail)
      headerFrom = "From: brown_library_easyborrow_system"
      headerReplyTo = 'Reply-To: interlibrary_loan@brown.edu'
      headerSubject = "Subject: Update on your 'easyBorrow' request"
    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'illiad_new_user' ):
      headerTo = "To: %s, interlibrary_loan@brown.edu, %s" % ( CIRC_ADMIN_EMAIL, ADMIN_EMAIL )
      headerFrom = "From: brown_library_easyborrow_system"
      headerReplyTo = 'Reply-To: %s' % CIRC_ADMIN_EMAIL
      headerSubject = "Subject: EASYBORROW_ALERT - Illiad new-user registration needed."
    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'login_failed_possibly_blocked' ):
      headerTo = "To: %s, interlibrary_loan@brown.edu, %s" % ( CIRC_ADMIN_EMAIL, ADMIN_EMAIL )
      headerFrom = "From: brown_library_easyborrow_system"
      headerReplyTo = 'Reply-To: %s' % CIRC_ADMIN_EMAIL
      headerSubject = "Subject: EASYBORROW_ALERT - Illiad request returned 'login_failed_possibly_blocked'"
    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'failure_no_sfx-link_to_illiad' ):
      headerTo = "To: %s, interlibrary_loan@brown.edu, %s" % ( CIRC_ADMIN_EMAIL, ADMIN_EMAIL )
      headerFrom = "From: brown_library_easyborrow_system"
      headerReplyTo = 'Reply-To: %s' % CIRC_ADMIN_EMAIL
      headerSubject = "Subject: EASYBORROW_ALERT - 'No sfx-link to illiad' intervention needed."
    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'unknown_illiad_failure' ):
      headerTo = 'To: %s' % ADMIN_EMAIL
      headerFrom = 'From: brown_library_easyborrow_system'
      headerReplyTo = 'Reply-To: %s' % ADMIN_EMAIL
      headerSubject = "Subject: EASYBORROW_ALERT - 'unknown_illiad_failure' result on request# 2"
    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'create_illiad_user_failed' ):
      headerTo = 'To: %s' % ADMIN_EMAIL # eventually: "To: CIRC_ADMIN_EMAIL, interlibrary_loan@brown.edu, ADMIN_EMAIL"
      headerFrom = 'From: brown_library_easyborrow_system'
      headerReplyTo = 'Reply-To: %s' % ADMIN_EMAIL
      headerSubject = "Subject: EASYBORROW_ALERT - 'create_illiad_user_failed'"
    else:
      headerTo = 'To: %s' % ADMIN_EMAIL
      headerFrom = 'From: brown_library_easyborrow_system'
      headerReplyTo = 'Reply-To: %s' % ADMIN_EMAIL
      headerSubject = "Subject: EASYBORROW_ALERT - 'unknown_situation'"

    headerInfo = headerTo + "\n" + headerFrom + "\n" + headerReplyTo + "\n" + headerSubject

    return headerInfo

    # end def prepFirstEmailHeader()



  def prepFirstEmailMessage_InRhode( self, itemInstance ):
    '''
    - Called by: UtilityCode.py->UtilityCode.sendEmail()
    - Purpose: Prepare message info for main InRhode email.
    '''

    message = '''
Greetings %s %s,

We've located the title '%s' and have ordered it for you. You'll be notified when it arrives.

Some useful information for your records:

- Title: '%s'
- Your 'easyBorrow' reference number: '%s'
- Ordered from service: 'InRhode'
- Notification of arrival will be sent to email address: '%s'

InRhode requests show up as regular Josiah requests, and you can check your Josiah requests at the link:
<https://josiah.brown.edu:443/patroninfo~S7>

If you have any questions, please contact the Rockefeller Library Gateway staff at rock@brown.edu or call 401/863-2165.

    ''' % (
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.itemTitle.encode( 'utf-8', 'replace' ),
      itemInstance.itemTitle.encode( 'utf-8', 'replace' ),
      itemInstance.requestNumber,
      itemInstance.genericAssignedUserEmail )

    return message

    # end def prepFirstEmailMessage_InRhode()



  def prepFirstEmailMessage_BorrowDirect( self, itemInstance ):
    '''
    - Called by: UtilityCode.py->UtilityCode.sendEmail()
    - Purpose: Prepare message info for main BorrowDirect email.
    '''

    message = '''
Greetings %s %s,

We've located the title '%s' and have ordered it for you. You'll be notified when it arrives.

Some useful information for your records:

- Title: '%s'
- Your 'easyBorrow' reference number: '%s'
- Ordered from service: 'BorrowDirect'
- Your BorrowDirect reference number: '%s'
- Notification of arrival will be sent to email address: '%s'

If you have any questions, contact the Library's Rockefeller Gateway staff at rock@brown.edu or call 863-2165.

    ''' % (
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.itemTitle,
      itemInstance.itemTitle,
      itemInstance.requestNumber,
      itemInstance.genericAssignedReferenceNumber,
      itemInstance.genericAssignedUserEmail )

    return message

    # end def prepFirstEmailMessage_BorrowDirect()



  def prepFirstEmailMessage_VirtualCatalog( self, itemInstance ):
    '''
    - Called by: UtilityCode.py->UtilityCode.sendEmail()
    - Purpose: Prepare message info for main VirtualCatalog email.
    '''

    message = '''
Greetings %s %s,

We've located the title '%s' and have ordered it for you. You'll be notified when it arrives.

Some useful information for your records:

- Title: '%s'
- Your 'easyBorrow' reference number: '%s'
- Ordered from service: 'VirtualCatalog'
- Your VirtualCatalog reference number: '%s'
- Notification of arrival will be sent to email address: '%s'

You can check your VirtualCatalog account at the link:
<http://blc.ursa.dynixasp.com/vcursa/patron_login.sh?ENTEREDPID=%s&ENTEREDLIB=BROWN>

If you have any questions, contact the Library's Rockefeller Gateway staff at rock@brown.edu or call 863-2165.

    ''' % (
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.itemTitle,
      itemInstance.itemTitle,
      itemInstance.requestNumber,
      itemInstance.genericAssignedReferenceNumber,
      itemInstance.genericAssignedUserEmail,
      itemInstance.patronBarcode )

    return message

    # end def prepFirstEmailMessage_VirtualCatalog()



  def prepFirstEmailMessage_Illiad_success( self, itemInstance ):
    '''
    - Called by: UtilityCode.py->UtilityCode.sendEmail()
    - Purpose: Prepare message info for main Illiad_success email.
    '''

    try:

      message = '''
  Greetings %s %s,

  We've located the title '%s' and have ordered it for you. You'll be notified when it arrives.

  Some useful information for your records:

  - Title: '%s'
  - Your 'easyBorrow' reference number: '%s'
  - Ordered from service: 'Illiad'
  - Your Illiad reference number: '%s'
  - Notification of arrival will be sent to email address: '%s'

  You can check your Illiad account at the link:
  <https://illiad.brown.edu/illiad/illiad.dll>

  If you have any questions, contact the Library's Interlibrary Loan office at interlibrary_loan@brown.edu or call 863-2169.

      ''' % (
        itemInstance.firstname,
        itemInstance.lastname,
        itemInstance.itemTitle,
        itemInstance.itemTitle,
        # itemInstance.itemTitle.decode( 'ascii', 'ignore' ).encode('ascii'),
        # itemInstance.itemTitle.decode( 'ascii', 'ignore' ).encode('ascii'),
        itemInstance.requestNumber,
        itemInstance.genericAssignedReferenceNumber,
        itemInstance.genericAssignedUserEmail )

    except Exception, e:
      self.updateLog( message="- in controller.uc.prepFirstEmailMessage_Illiad_success(); exception is: %s; itemInstance.__dict__ is: %s" % (e, itemInstance.__dict__), message_importance='high', identifier='unavailable' )

    return message

    # end def prepFirstEmailMessage_Illiad_success()



  def prepFirstEmailMessage_Illiad_illiadNewUser( self, itemInstance ):
    '''
    - Called by: UtilityCode.py->UtilityCode.sendEmail()
    - Purpose: Prepare message info for main Illiad_illiadNewUser email.
    '''

    message = '''
ILL staff,

The easyBorrow automated borrowing system has attempted to get the item: '%s' through Illiad for the patron: %s %s.

However, the patron doesn't appear to be registered.

(1) Patron info...
- First name: %s
- Last name: %s
- Patron login authId: %s
- Patron barcode: %s
- Email address: %s
- Campus address: %s
- Telephone Number: %s
- Department: %s
- Patron type (pcode3): %s

(2) Item info...
- Title: %s
- Item link (complete item information): <http://worldcat.org/oclc/%s>

(3) Special user-requests...
- Alternate Edition Acceptable: %s
- Volume(s) Specification: %s

(4) Other info...
- easyBorrow transaction number: %s

[end]

    ''' % (
      itemInstance.itemTitle,
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.illiadAssignedAuthId,
      itemInstance.patronBarcode,
      itemInstance.patronEmail,
      itemInstance.patron_api_address,
      itemInstance.patron_api_telephone,
      itemInstance.patron_api_dept,
      itemInstance.patron_api_pcode3,
      itemInstance.patronId,
      itemInstance.itemTitle,
      itemInstance.oclcNumber,
      itemInstance.alternateEditionPreference,
      itemInstance.volumesPreference,
      itemInstance.itemDbId )

    return message

    # end def prepFirstEmailMessage_Illiad_illiadNewUser()



  def prepFirstEmailMessage_Illiad_createIlliadUserFailed( self, itemInstance ):
    '''
    - Called by: UtilityCode.py->UtilityCode.sendEmail()
    - Purpose: Prepare message info for main Illiad_createIlliadUserFailed email.
    '''

    message = '''
ILL staff,

The easyBorrow automated borrowing attempted to automatically register, in Illiad, the patron: %s %s.

However, the auto-registration was unsuccessful. Please register this user
manually and then click the 'try-again' button for this transaction.

(1) Patron info...
- First name: %s
- Last name: %s
- Patron login authId: %s
- Patron barcode: %s
- Email address: %s
- Campus address: %s
- Telephone Number: %s
- Department: %s
- Patron type (pcode3): %s

(2) Other info...
- easyBorrow transaction number: %s

[end]

    ''' % (
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.illiadAssignedAuthId,
      itemInstance.patronBarcode,
      itemInstance.patronEmail,
      itemInstance.patron_api_address,
      itemInstance.patron_api_telephone,
      itemInstance.patron_api_dept,
      itemInstance.patron_api_pcode3,
      itemInstance.patronId,
      itemInstance.itemDbId )

    return message

    # end def prepFirstEmailMessage_Illiad_createIlliadUserFailed()



  def prepFirstEmailMessage_Illiad_loginFailedPossiblyBlocked( itemInstance ):
    '''
    - Called by: UtilityCode.py->UtilityCode.sendEmail()
    - Purpose: Prepare message info for main Illiad_loginFailedPossiblyBlocked email.
    '''

    message = '''
ILL staff,

The easyBorrow automated borrowing system has attempted to get the item: '%s' through Illiad for the patron: %s %s.

However, the easyBorrow couldn't auto-log this user into Illiad, likely because the user is blocked. This request is on hold.

If you unblock the user, please go to the url above and click the 'try-again' button.

[end]

    ''' % (
      itemInstance.itemTitle,
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.itemDbId )

    return message

    # end def prepFirstEmailMessage_Illiad_loginFailedPossiblyBlocked()



  def prepFirstEmailMessage_Illiad_failureNoSfxLinkToIlliad( self, itemInstance ):
    '''
    - Called by: UtilityCode.py->UtilityCode.sendEmail()
    - Purpose: Prepare message info for main Illiad_failureNoSfxLinkToIlliad email.
    '''

    message = '''
ILL staff,

The easyBorrow automated borrowing system has attempted to get the item: '%s' through Illiad for the patron: %s %s.

However, the easyBorrow system can't find a link to Illiad on the sfx-page, which is likely displaying the 'Multiple Object Menu'.

(1) Patron info...
- First name: %s
- Last name: %s
- Patron login authId: %s
- Patron barcode: %s
- Email address: %s
- Campus address: %s
- Telephone Number: %s
- Department: %s
- Patron type (pcode3): %s

(2) Item info...
- Title: %s
- Item link (complete item information): <http://worldcat.org/oclc/%s>

(3) Special user-requests...
- Alternate Edition Acceptable: %s
- Volume(s) Specification: %s

(4) Other info...
- easyBorrow transaction number: %s

[end]

    ''' % (
      itemInstance.itemTitle,
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.illiadAssignedAuthId,
      itemInstance.patronBarcode,
      itemInstance.patronEmail,
      itemInstance.patron_api_address,
      itemInstance.patron_api_telephone,
      itemInstance.patron_api_dept,
      itemInstance.patron_api_pcode3,
      itemInstance.patronId,
      itemInstance.itemTitle,
      itemInstance.oclcNumber,
      itemInstance.alternateEditionPreference,
      itemInstance.volumesPreference,
      itemInstance.itemDbId )

    return message

    # end def prepFirstEmailMessage_Illiad_failureNoSfxLinkToIlliad()



  def prepFirstEmailMessage_Illiad_illiadUnknownFailure( self, itemInstance ):
    '''
    - Called by: UtilityCode.py->UtilityCode.sendEmail()
    - Purpose: Prepare message info for main Illiad_illiadUnknownFailure email.
    '''

    message = '''
BJD,

The easyBorrow automated borrowing encountered a problem requesting via Illiad the item: '%s' through Illiad for the patron: %s %s.

(1) Patron info...
- First name: %s
- Last name: %s
- Patron login authId: %s
- Patron barcode: %s
- Email address: %s
- Campus address: %s
- Telephone Number: %s
- Department: %s
- Patron type (pcode3): %s

(2) Item info...
- Title: %s
- Item link (complete item information): <http://worldcat.org/oclc/%s>

(3) Special user-requests...
- Alternate Edition Acceptable: %s
- Volume(s) Specification: %s

(4) Other info...
- easyBorrow transaction number: %s

[end]

    ''' % (
      itemInstance.itemTitle,
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.firstname,
      itemInstance.lastname,
      itemInstance.illiadAssignedAuthId,
      itemInstance.patronBarcode,
      itemInstance.patronEmail,
      itemInstance.patron_api_address,
      itemInstance.patron_api_telephone,
      itemInstance.patron_api_dept,
      itemInstance.patron_api_pcode3,
      itemInstance.patronId,
      itemInstance.itemTitle,
      itemInstance.oclcNumber,
      itemInstance.alternateEditionPreference,
      itemInstance.volumesPreference,
      itemInstance.itemDbId )

    return message

    # end def prepFirstEmailMessage_Illiad_illiadUnknownFailure()



  def prepFirstEmailRecipientList( self, itemInstance, eb_request_number ):
    '''
    - Called by: UtilityCode.py->UtilityCode.sendEmail()
    - Purpose: Prepare recipient list for main email.
    '''

    try:
      ADMIN_EMAIL = unicode( os.environ[u'ezbCTL__ADMIN_EMAIL'] )
      CIRC_ADMIN_EMAIL = unicode( os.environ[u'ezbCTL__CIRC_ADMIN_EMAIL'] )
      if( itemInstance.currentlyActiveService == 'inRhode' and itemInstance.requestSuccessStatus == 'success' ):
        recipientList = [itemInstance.patronEmail]
      elif( itemInstance.currentlyActiveService == 'borrowDirect' and itemInstance.requestSuccessStatus == 'success' ):
        recipientList = [itemInstance.patronEmail]
      elif( itemInstance.currentlyActiveService == 'virtualCatalog' and itemInstance.requestSuccessStatus == 'success' ):
        recipientList = [itemInstance.patronEmail]
      elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'success' ):
        recipientList = [itemInstance.patronEmail]
      elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'illiad_new_user' ):
        recipientList = ["interlibrary_loan@brown.edu", CIRC_ADMIN_EMAIL, ADMIN_EMAIL ]
      elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'login_failed_possibly_blocked' ):
        recipientList = ["interlibrary_loan@brown.edu", CIRC_ADMIN_EMAIL, ADMIN_EMAIL ]
      elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'failure_no_sfx-link_to_illiad' ):
        recipientList = ["interlibrary_loan@brown.edu", CIRC_ADMIN_EMAIL, ADMIN_EMAIL ]
      elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'illiad_unknown_failure' ):
        recipientList = [ADMIN_EMAIL]
      elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'create_illiad_user_failed' ):
        recipientList = [CIRC_ADMIN_EMAIL, ADMIN_EMAIL] # will really eventually be: ["interlibrary_loan@brown.edu", CIRC_ADMIN_EMAIL, ADMIN_EMAIL ]
      else:
        recipientList = [ADMIN_EMAIL]
      return recipientList

    except:
      self.updateLog(
        message='- in UtilityCode.prepFirstEmailRecipientList; error-type - %s; error-message - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, ),
        message_importance='high',
        identifier=eb_request_number )

    # end def prepFirstEmailRecipientList()



  def returnExceptionMessage(self):
    '''
    - Only called by UtilityCodeTest.py
    - Purpose: to check syntax for exceptions for error-logging.
    '''

    import sys
    try:
      1/0
    except Exception, e:
      return 'error-type - %s; error-message - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, )

    # end def returnExceptionMessage()



  def sendEmail( self, itemInstance, eb_request_number ):

    ## setup ##

    import os
    import smtplib
    import sys
    import time

    ADMIN_EMAIL = unicode( os.environ[u'ezbCTL__ADMIN_EMAIL'] )
    smtpServer = "mail-relay.brown.edu"
    mailSession = smtplib.SMTP(smtpServer)

    # ## hack the title to avoid encoding issues -- TO-DO: handle this appropriately ##
    # itemInstance.itemTitle = itemInstance.itemTitle.decode( 'ascii', 'ignore' ).encode('ascii')

    ## header info ##

    headerInfo = self.prepFirstEmailHeader( itemInstance )

    ## message ##

    self.updateLog( message='- in controller.uc.sendEmail(); preparing email; currentlyActiveService is: %s; requestSuccessStatus is: %s' % (itemInstance.currentlyActiveService, itemInstance.requestSuccessStatus), message_importance='low', identifier=eb_request_number )

    if ( itemInstance.currentlyActiveService == 'inRhode' ):
      self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; in 'inRhode'", message_importance='low', identifier=eb_request_number )
      message = self.prepFirstEmailMessage_InRhode( itemInstance )

    elif( itemInstance.currentlyActiveService == 'borrowDirect' ):
      self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; in 'borrowDirect'", message_importance='low', identifier=eb_request_number )
      message = self.prepFirstEmailMessage_BorrowDirect( itemInstance )

    elif( itemInstance.currentlyActiveService == 'virtualCatalog' ):
      self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; in 'virtualCatalog'", message_importance='low', identifier=eb_request_number)
      message = self.prepFirstEmailMessage_VirtualCatalog( itemInstance )

    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'success' ):
      self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; in 'illiad->success'", message_importance='low', identifier=eb_request_number )
      try:
        message = self.prepFirstEmailMessage_Illiad_success( itemInstance )
        self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; in 'illiad->success'; message is: %s" % message, message_importance='low', identifier=eb_request_number )
      except Exception, e:
        self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; in 'illiad->success'; exception is: %s" % e, message_importance='high', identifier=eb_request_number )

    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'illiad_new_user' ):
      self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; in 'illiad->illiad_new_user'", message_importance='low', identifier=eb_request_number )
      message = self.prepFirstEmailMessage_Illiad_illiadNewUser( itemInstance )
      self.updateLog( message="- in controller.uc.sendEmail(); in illiad new_user if-statement; *staff* 'new-user' message composed", message_importance='low', identifier=eb_request_number )

    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'create_illiad_user_failed' ):
      self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; in 'create_illiad_user_failed'", message_importance='low', identifier=eb_request_number )
      message = self.prepFirstEmailMessage_Illiad_createIlliadUserFailed( itemInstance )
      self.updateLog( message="- in controller.uc.sendEmail(); in illiad new_user if-statement; *staff* 'new-user' message composed", message_importance='low', identifier=eb_request_number )

    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'login_failed_possibly_blocked' ):
      self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; in 'illiad->login_failed_possibly_blocked'", message_importance='low', identifier=eb_request_number )
      message = self.prepFirstEmailMessage_Illiad_loginFailedPossiblyBlocked( itemInstance )
      self.updateLog( message="- in controller.uc.sendEmail(); in illiad login_failed_possibly_blocked if-statement; *staff* message composed", message_importance='low', identifier=eb_request_number )

    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'failure_no_sfx-link_to_illiad' ):
      self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; in 'illiad->failure_no_sfx-link_to_illiad'", message_importance='low', identifier=eb_request_number )
      message = self.prepFirstEmailMessage_Illiad_failureNoSfxLinkToIlliad( itemInstance )
      self.updateLog( message="- in controller.uc.sendEmail(); in illiad new_user if-statement; *staff* 'no-sfx-link' message composed", message_importance='low', identifier=eb_request_number )

    elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'illiad_unknown_failure' ):
      self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; in 'illiad->illiad_unknown_failure'", message_importance='low', identifier=eb_request_number )
      message = self.prepFirstEmailMessage_Illiad_illiadUnknownFailure( itemInstance )
      self.updateLog( message="- in controller.uc.sendEmail(); in 'illiad->illiad_unknown_failure' if-statement; message to admin composed", message_importance='low', identifier=eb_request_number )

    else:
      self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; default unhandled situation", message_importance='low', identifier=eb_request_number )
      message = '''BJD - handle this situation.'''
      self.updateLog( message="- in controller.uc.sendEmail(); sendMail_if-activeService; default message to admin composed", message_importance='low', identifier=eb_request_number)

      # end of message-body if statements

    ## complete message ##

    fullMessage = headerInfo + "\n" + message
    self.updateLog( message="- in controller.uc.sendEmail(); fullMessage prepared", message_importance='low', identifier=eb_request_number)

    self.logger.debug( u'%s -- type(message), `%s`' % (itemInstance.log_identifier, type(message)) )  # unicode -- TODO, remove these log-entries 2015-June-30 if problem solved
    self.logger.debug( u'%s -- type(fullMessage), `%s`' % (itemInstance.log_identifier, type(fullMessage)) )  # unicode
    fullMessage = fullMessage.encode( 'utf-8', 'ignore' )

    ## non-display info -- NOTE: this really controls who it goes to, not the 'To:' info above. ##

    sender = ADMIN_EMAIL
    try:
      recipientList = self.prepFirstEmailRecipientList( itemInstance, eb_request_number )
    except Exception, e:
      self.updateLog(
        message='- in controller.uc.sendEmail(); error-type - %s; error-message - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, ),
        message_importance='high',
        identifier=eb_request_number )

    self.updateLog( message="- in controller.uc.sendEmail(); sender and recipientList prepared", message_importance='low', identifier=eb_request_number)

    ## try the send ##

    returnValue = "init"
    try:
      self.updateLog(  message='- in controller.uc.sendEmail(); email attempt starting', message_importance='low', identifier=eb_request_number )
      smtpResult = mailSession.sendmail(sender, recipientList, fullMessage)
      self.updateLog( message='- in controller.uc.sendEmail(); email sent successfully', message_importance='low', identifier=eb_request_number )
      returnValue = 'success' # tentatively
    except:
      mailSession.quit()
      self.updateLog(  message='- in controller.uc.sendEmail(); attempt to send email failed with errors', message_importance='low', identifier=eb_request_number )
      self.updateLog(  message='- in controller.uc.sendEmail(); the errors: %s' % smtpResult, message_importance='low', identifier=eb_request_number )
      try:
        time.sleep(5) # 5 seconds of peace to recharge karma
        self.updateLog(  message='- in controller.uc.sendEmail(); second email attempt starting' )
        mailSession2 = smtplib.SMTP(smtpServer)
        smtpResult2 = mailSession2.sendmail(sender, recipientList, fullMessage)
        self.updateLog( message='- in controller.uc.sendEmail(); second email sent successfully', message_importance='low', identifier=eb_request_number )
      except:
        mailSession2.quit()
        self.updateLog(  message='- in controller.uc.sendEmail(); attempt to send second email failed with errors', message_importance='low', identifier=eb_request_number )
        self.updateLog(  message='- in controller.uc.sendEmail(); the errors: first, <<%s>>; and second, <<%s>>.' % (smtpResult, smtpResult2), message_importance='low', identifier=eb_request_number )
        returnValue = 'failure'
      else:
        mailSession2.quit()
        returnValue = "success"
        self.updateLog( message='- in controller.uc.sendEmail(); second mail session quit normally', message_importance='low', identifier=eb_request_number )
    else:
      mailSession.quit()
      self.updateLog(message='- in controller.uc.sendEmail(); mailSession1 quit normally', message_importance='low', identifier=eb_request_number )

    return returnValue

    # end function sendEmail



# bottom
