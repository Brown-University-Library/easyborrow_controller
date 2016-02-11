# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging, os, smtplib, sys, time, urllib, urllib2
# import MySQLdb
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


class UtilityCode( object ):


  def __init__( self, logger ):
    self.timeToFormat = ""
    self.log = ""
    self.log_identifier = ''  # set by controller.run_code()
    self.logger = logger  # set by Controller() or Item()


  # def prepFirstEmailHeader( self, itemInstance ):
  #   '''
  #   - Called by: UtilityCode.py->UtilityCode.sendEmail()
  #   - Purpose: Prepare header info for main email.
  #   '''
  #   ADMIN_EMAIL = settings.ADMIN_EMAIL
  #   CIRC_ADMIN_EMAIL = settings.CIRC_ADMIN_EMAIL

  #   if ( itemInstance.currentlyActiveService == 'inRhode' and itemInstance.requestSuccessStatus == 'success' ):
  #     headerTo = "To: %s" % (itemInstance.patronEmail)
  #     headerFrom = "From: brown_library_easyborrow_system"
  #     headerReplyTo = 'Reply-To: rock@brown.edu'
  #     headerSubject = "Subject: Update on your 'easyBorrow' request"
  #   elif( itemInstance.currentlyActiveService == 'borrowDirect' and itemInstance.requestSuccessStatus == 'success' ):
  #     headerTo = "To: %s" % (itemInstance.patronEmail)
  #     headerFrom = "From: brown_library_easyborrow_system"
  #     headerReplyTo = 'Reply-To: rock@brown.edu'
  #     headerSubject = "Subject: Update on your 'easyBorrow' request"
  #   elif( itemInstance.currentlyActiveService == 'virtualCatalog' and itemInstance.requestSuccessStatus == 'success' ):
  #     headerTo = "To: %s" % (itemInstance.patronEmail)
  #     headerFrom = "From: brown_library_easyborrow_system"
  #     headerReplyTo = 'Reply-To: rock@brown.edu'
  #     headerSubject = "Subject: Update on your 'easyBorrow' request"
  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'success' ):
  #     headerTo = "To: %s" % (itemInstance.patronEmail)
  #     headerFrom = "From: brown_library_easyborrow_system"
  #     headerReplyTo = 'Reply-To: interlibrary_loan@brown.edu'
  #     headerSubject = "Subject: Update on your 'easyBorrow' request"
  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'illiad_new_user' ):
  #     headerTo = "To: %s, interlibrary_loan@brown.edu, %s" % ( CIRC_ADMIN_EMAIL, ADMIN_EMAIL )
  #     headerFrom = "From: brown_library_easyborrow_system"
  #     headerReplyTo = 'Reply-To: %s' % CIRC_ADMIN_EMAIL
  #     headerSubject = "Subject: EASYBORROW_ALERT - Illiad new-user registration needed."
  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'login_failed_possibly_blocked' ):
  #     headerTo = "To: %s, interlibrary_loan@brown.edu, %s" % ( CIRC_ADMIN_EMAIL, ADMIN_EMAIL )
  #     headerFrom = "From: brown_library_easyborrow_system"
  #     headerReplyTo = 'Reply-To: %s' % CIRC_ADMIN_EMAIL
  #     headerSubject = "Subject: EASYBORROW_ALERT - Illiad request returned 'login_failed_possibly_blocked'"
  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'failure_no_sfx-link_to_illiad' ):
  #     headerTo = "To: %s, interlibrary_loan@brown.edu, %s" % ( CIRC_ADMIN_EMAIL, ADMIN_EMAIL )
  #     headerFrom = "From: brown_library_easyborrow_system"
  #     headerReplyTo = 'Reply-To: %s' % CIRC_ADMIN_EMAIL
  #     headerSubject = "Subject: EASYBORROW_ALERT - 'No sfx-link to illiad' intervention needed."
  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'unknown_illiad_failure' ):
  #     headerTo = 'To: %s' % ADMIN_EMAIL
  #     headerFrom = 'From: brown_library_easyborrow_system'
  #     headerReplyTo = 'Reply-To: %s' % ADMIN_EMAIL
  #     headerSubject = "Subject: EASYBORROW_ALERT - 'unknown_illiad_failure' result on request# 2"
  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'create_illiad_user_failed' ):
  #     headerTo = 'To: %s' % ADMIN_EMAIL # eventually: "To: CIRC_ADMIN_EMAIL, interlibrary_loan@brown.edu, ADMIN_EMAIL"
  #     headerFrom = 'From: brown_library_easyborrow_system'
  #     headerReplyTo = 'Reply-To: %s' % ADMIN_EMAIL
  #     headerSubject = "Subject: EASYBORROW_ALERT - 'create_illiad_user_failed'"
  #   else:
  #     headerTo = 'To: %s' % ADMIN_EMAIL
  #     headerFrom = 'From: brown_library_easyborrow_system'
  #     headerReplyTo = 'Reply-To: %s' % ADMIN_EMAIL
  #     headerSubject = "Subject: EASYBORROW_ALERT - 'unknown_situation'"

  #   headerInfo = headerTo + "\n" + headerFrom + "\n" + headerReplyTo + "\n" + headerSubject

  #   return headerInfo

  #   # end def prepFirstEmailHeader()



#   def prepFirstEmailMessage_InRhode( self, itemInstance ):
#     '''
#     - Called by: UtilityCode.py->UtilityCode.sendEmail()
#     - Purpose: Prepare message info for main InRhode email.
#     '''

#     message = '''
# Greetings %s %s,

# We've located the title '%s' and have ordered it for you. You'll be notified when it arrives.

# Some useful information for your records:

# - Title: '%s'
# - Your 'easyBorrow' reference number: '%s'
# - Ordered from service: 'InRhode'
# - Notification of arrival will be sent to email address: '%s'

# InRhode requests show up as regular Josiah requests, and you can check your Josiah requests at the link:
# <https://josiah.brown.edu:443/patroninfo~S7>

# If you have any questions, please contact the Rockefeller Library Gateway staff at rock@brown.edu or call 401/863-2165.

#     ''' % (
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.itemTitle.encode( 'utf-8', 'replace' ),
#       itemInstance.itemTitle.encode( 'utf-8', 'replace' ),
#       itemInstance.requestNumber,
#       itemInstance.genericAssignedUserEmail )

#     return message

#     # end def prepFirstEmailMessage_InRhode()



#   def prepFirstEmailMessage_BorrowDirect( self, itemInstance ):
#     '''
#     - Called by: UtilityCode.py->UtilityCode.sendEmail()
#     - Purpose: Prepare message info for main BorrowDirect email.
#     '''

#     message = '''
# Greetings %s %s,

# We've located the title '%s' and have ordered it for you. You'll be notified when it arrives.

# Some useful information for your records:

# - Title: '%s'
# - Your 'easyBorrow' reference number: '%s'
# - Ordered from service: 'BorrowDirect'
# - Your BorrowDirect reference number: '%s'
# - Notification of arrival will be sent to email address: '%s'

# If you have any questions, contact the Library's Rockefeller Gateway staff at rock@brown.edu or call 863-2165.

#     ''' % (
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.itemTitle,
#       itemInstance.itemTitle,
#       itemInstance.requestNumber,
#       itemInstance.genericAssignedReferenceNumber,
#       itemInstance.genericAssignedUserEmail )

#     return message

#     # end def prepFirstEmailMessage_BorrowDirect()



#   def prepFirstEmailMessage_VirtualCatalog( self, itemInstance ):
#     '''
#     - Called by: UtilityCode.py->UtilityCode.sendEmail()
#     - Purpose: Prepare message info for main VirtualCatalog email.
#     '''

#     message = '''
# Greetings %s %s,

# We've located the title '%s' and have ordered it for you. You'll be notified when it arrives.

# Some useful information for your records:

# - Title: '%s'
# - Your 'easyBorrow' reference number: '%s'
# - Ordered from service: 'VirtualCatalog'
# - Your VirtualCatalog reference number: '%s'
# - Notification of arrival will be sent to email address: '%s'

# You can check your VirtualCatalog account at the link:
# <http://blc.ursa.dynixasp.com/vcursa/patron_login.sh?ENTEREDPID=%s&ENTEREDLIB=BROWN>

# If you have any questions, contact the Library's Rockefeller Gateway staff at rock@brown.edu or call 863-2165.

#     ''' % (
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.itemTitle,
#       itemInstance.itemTitle,
#       itemInstance.requestNumber,
#       itemInstance.genericAssignedReferenceNumber,
#       itemInstance.genericAssignedUserEmail,
#       itemInstance.patronBarcode )

#     return message

#     # end def prepFirstEmailMessage_VirtualCatalog()



  # def prepFirstEmailMessage_Illiad_success( self, itemInstance ):
  #   '''
  #   - Called by: UtilityCode.py->UtilityCode.sendEmail()
  #   - Purpose: Prepare message info for main Illiad_success email.
  #   '''

  #   try:

  #     message = '''
  # Greetings %s %s,

  # We've located the title '%s' and have ordered it for you. You'll be notified when it arrives.

  # Some useful information for your records:

  # - Title: '%s'
  # - Your 'easyBorrow' reference number: '%s'
  # - Ordered from service: 'Illiad'
  # - Your Illiad reference number: '%s'
  # - Notification of arrival will be sent to email address: '%s'

  # You can check your Illiad account at the link:
  # <https://illiad.brown.edu/illiad/illiad.dll>

  # If you have any questions, contact the Library's Interlibrary Loan office at interlibrary_loan@brown.edu or call 863-2169.

  #     ''' % (
  #       itemInstance.firstname,
  #       itemInstance.lastname,
  #       itemInstance.itemTitle,
  #       itemInstance.itemTitle,
  #       # itemInstance.itemTitle.decode( 'ascii', 'ignore' ).encode('ascii'),
  #       # itemInstance.itemTitle.decode( 'ascii', 'ignore' ).encode('ascii'),
  #       itemInstance.requestNumber,
  #       itemInstance.genericAssignedReferenceNumber,
  #       itemInstance.genericAssignedUserEmail )

  #   except Exception, e:
  #     web_logger.post_message( message='- in classes.UtilityCode.prepFirstEmailMessage_Illiad_success(); exception is: %s' % unicode(repr(e)), identifier='unavailable', importance='error' )

  #   return message

  #   # end def prepFirstEmailMessage_Illiad_success()



#   def prepFirstEmailMessage_Illiad_illiadNewUser( self, itemInstance ):
#     '''
#     - Called by: UtilityCode.py->UtilityCode.sendEmail()
#     - Purpose: Prepare message info for main Illiad_illiadNewUser email.
#     '''

#     message = '''
# ILL staff,

# The easyBorrow automated borrowing system has attempted to get the item: '%s' through Illiad for the patron: %s %s.

# However, the patron doesn't appear to be registered.

# (1) Patron info...
# - First name: %s
# - Last name: %s
# - Patron login authId: %s
# - Patron barcode: %s
# - Email address: %s
# - Campus address: %s
# - Telephone Number: %s
# - Department: %s
# - Patron type (pcode3): %s

# (2) Item info...
# - Title: %s
# - Item link (complete item information): <http://worldcat.org/oclc/%s>

# (3) Special user-requests...
# - Alternate Edition Acceptable: %s
# - Volume(s) Specification: %s

# (4) Other info...
# - easyBorrow transaction number: %s

# [end]

#     ''' % (
#       itemInstance.itemTitle,
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.illiadAssignedAuthId,
#       itemInstance.patronBarcode,
#       itemInstance.patronEmail,
#       itemInstance.patron_api_address,
#       itemInstance.patron_api_telephone,
#       itemInstance.patron_api_dept,
#       itemInstance.patron_api_pcode3,
#       itemInstance.patronId,
#       itemInstance.itemTitle,
#       itemInstance.oclcNumber,
#       itemInstance.alternateEditionPreference,
#       itemInstance.volumesPreference,
#       itemInstance.itemDbId )

#     return message

#     # end def prepFirstEmailMessage_Illiad_illiadNewUser()



#   def prepFirstEmailMessage_Illiad_createIlliadUserFailed( self, itemInstance ):
#     '''
#     - Called by: UtilityCode.py->UtilityCode.sendEmail()
#     - Purpose: Prepare message info for main Illiad_createIlliadUserFailed email.
#     '''

#     message = '''
# ILL staff,

# The easyBorrow automated borrowing attempted to automatically register, in Illiad, the patron: %s %s.

# However, the auto-registration was unsuccessful. Please register this user
# manually and then click the 'try-again' button for this transaction.

# (1) Patron info...
# - First name: %s
# - Last name: %s
# - Patron login authId: %s
# - Patron barcode: %s
# - Email address: %s
# - Campus address: %s
# - Telephone Number: %s
# - Department: %s
# - Patron type (pcode3): %s

# (2) Other info...
# - easyBorrow transaction number: %s

# [end]

#     ''' % (
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.illiadAssignedAuthId,
#       itemInstance.patronBarcode,
#       itemInstance.patronEmail,
#       itemInstance.patron_api_address,
#       itemInstance.patron_api_telephone,
#       itemInstance.patron_api_dept,
#       itemInstance.patron_api_pcode3,
#       itemInstance.patronId,
#       itemInstance.itemDbId )

#     return message

#     # end def prepFirstEmailMessage_Illiad_createIlliadUserFailed()



#   def prepFirstEmailMessage_Illiad_loginFailedPossiblyBlocked( itemInstance ):
#     '''
#     - Called by: UtilityCode.py->UtilityCode.sendEmail()
#     - Purpose: Prepare message info for main Illiad_loginFailedPossiblyBlocked email.
#     '''

#     message = '''
# ILL staff,

# The easyBorrow automated borrowing system has attempted to get the item: '%s' through Illiad for the patron: %s %s.

# However, the easyBorrow couldn't auto-log this user into Illiad, likely because the user is blocked. This request is on hold.

# If you unblock the user, please go to the url above and click the 'try-again' button.

# [end]

#     ''' % (
#       itemInstance.itemTitle,
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.itemDbId )

#     return message

#     # end def prepFirstEmailMessage_Illiad_loginFailedPossiblyBlocked()



#   def prepFirstEmailMessage_Illiad_failureNoSfxLinkToIlliad( self, itemInstance ):
#     '''
#     - Called by: UtilityCode.py->UtilityCode.sendEmail()
#     - Purpose: Prepare message info for main Illiad_failureNoSfxLinkToIlliad email.
#     '''

#     message = '''
# ILL staff,

# The easyBorrow automated borrowing system has attempted to get the item: '%s' through Illiad for the patron: %s %s.

# However, the easyBorrow system can't find a link to Illiad on the sfx-page, which is likely displaying the 'Multiple Object Menu'.

# (1) Patron info...
# - First name: %s
# - Last name: %s
# - Patron login authId: %s
# - Patron barcode: %s
# - Email address: %s
# - Campus address: %s
# - Telephone Number: %s
# - Department: %s
# - Patron type (pcode3): %s

# (2) Item info...
# - Title: %s
# - Item link (complete item information): <http://worldcat.org/oclc/%s>

# (3) Special user-requests...
# - Alternate Edition Acceptable: %s
# - Volume(s) Specification: %s

# (4) Other info...
# - easyBorrow transaction number: %s

# [end]

#     ''' % (
#       itemInstance.itemTitle,
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.illiadAssignedAuthId,
#       itemInstance.patronBarcode,
#       itemInstance.patronEmail,
#       itemInstance.patron_api_address,
#       itemInstance.patron_api_telephone,
#       itemInstance.patron_api_dept,
#       itemInstance.patron_api_pcode3,
#       itemInstance.patronId,
#       itemInstance.itemTitle,
#       itemInstance.oclcNumber,
#       itemInstance.alternateEditionPreference,
#       itemInstance.volumesPreference,
#       itemInstance.itemDbId )

#     return message

#     # end def prepFirstEmailMessage_Illiad_failureNoSfxLinkToIlliad()



#   def prepFirstEmailMessage_Illiad_illiadUnknownFailure( self, itemInstance ):
#     '''
#     - Called by: UtilityCode.py->UtilityCode.sendEmail()
#     - Purpose: Prepare message info for main Illiad_illiadUnknownFailure email.
#     '''

#     message = '''
# BJD,

# The easyBorrow automated borrowing encountered a problem requesting via Illiad the item: '%s' through Illiad for the patron: %s %s.

# (1) Patron info...
# - First name: %s
# - Last name: %s
# - Patron login authId: %s
# - Patron barcode: %s
# - Email address: %s
# - Campus address: %s
# - Telephone Number: %s
# - Department: %s
# - Patron type (pcode3): %s

# (2) Item info...
# - Title: %s
# - Item link (complete item information): <http://worldcat.org/oclc/%s>

# (3) Special user-requests...
# - Alternate Edition Acceptable: %s
# - Volume(s) Specification: %s

# (4) Other info...
# - easyBorrow transaction number: %s

# [end]

#     ''' % (
#       itemInstance.itemTitle,
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.firstname,
#       itemInstance.lastname,
#       itemInstance.illiadAssignedAuthId,
#       itemInstance.patronBarcode,
#       itemInstance.patronEmail,
#       itemInstance.patron_api_address,
#       itemInstance.patron_api_telephone,
#       itemInstance.patron_api_dept,
#       itemInstance.patron_api_pcode3,
#       itemInstance.patronId,
#       itemInstance.itemTitle,
#       itemInstance.oclcNumber,
#       itemInstance.alternateEditionPreference,
#       itemInstance.volumesPreference,
#       itemInstance.itemDbId )

#     return message

#     # end def prepFirstEmailMessage_Illiad_illiadUnknownFailure()



  # def prepFirstEmailRecipientList( self, itemInstance, eb_request_number ):
  #   '''
  #   - Called by: UtilityCode.py->UtilityCode.sendEmail()
  #   - Purpose: Prepare recipient list for main email.
  #   '''

  #   try:
  #     ADMIN_EMAIL = settings.ADMIN_EMAIL
  #     CIRC_ADMIN_EMAIL = settings.CIRC_ADMIN_EMAIL
  #     if( itemInstance.currentlyActiveService == 'inRhode' and itemInstance.requestSuccessStatus == 'success' ):
  #       recipientList = [itemInstance.patronEmail]
  #     elif( itemInstance.currentlyActiveService == 'borrowDirect' and itemInstance.requestSuccessStatus == 'success' ):
  #       recipientList = [itemInstance.patronEmail]
  #     elif( itemInstance.currentlyActiveService == 'virtualCatalog' and itemInstance.requestSuccessStatus == 'success' ):
  #       recipientList = [itemInstance.patronEmail]
  #     elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'success' ):
  #       recipientList = [itemInstance.patronEmail]
  #     elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'illiad_new_user' ):
  #       recipientList = ["interlibrary_loan@brown.edu", CIRC_ADMIN_EMAIL, ADMIN_EMAIL ]
  #     elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'login_failed_possibly_blocked' ):
  #       recipientList = ["interlibrary_loan@brown.edu", CIRC_ADMIN_EMAIL, ADMIN_EMAIL ]
  #     elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'failure_no_sfx-link_to_illiad' ):
  #       recipientList = ["interlibrary_loan@brown.edu", CIRC_ADMIN_EMAIL, ADMIN_EMAIL ]
  #     elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'illiad_unknown_failure' ):
  #       recipientList = [ADMIN_EMAIL]
  #     elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'create_illiad_user_failed' ):
  #       recipientList = [CIRC_ADMIN_EMAIL, ADMIN_EMAIL] # will really eventually be: ["interlibrary_loan@brown.edu", CIRC_ADMIN_EMAIL, ADMIN_EMAIL ]
  #     else:
  #       recipientList = [ADMIN_EMAIL]
  #     return recipientList

  #   except:
  #     web_logger.post_message( message='- in classes.UtilityCode.prepFirstEmailRecipientList(); error-type - %s; error-message - %s; line-number - %s' % (sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno), identifier=eb_request_number, importance='error' )

  #   # end def prepFirstEmailRecipientList()



  def returnExceptionMessage(self):
    '''
    - Only called by UtilityCodeTest.py
    - Purpose: to check syntax for exceptions for error-logging.
    '''

    try:
      1/0
    except Exception, e:
      return 'error-type - %s; error-message - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, )

    # end def returnExceptionMessage()



  # def sendEmail( self, itemInstance, eb_request_number ):

  #   ## setup ##

  #   ADMIN_EMAIL = settings.ADMIN_EMAIL
  #   smtpServer = "mail-relay.brown.edu"
  #   mailSession = smtplib.SMTP(smtpServer)

  #   # ## hack the title to avoid encoding issues -- TO-DO: handle this appropriately ##
  #   # itemInstance.itemTitle = itemInstance.itemTitle.decode( 'ascii', 'ignore' ).encode('ascii')

  #   ## header info ##

  #   headerInfo = self.prepFirstEmailHeader( itemInstance )

  #   ## message ##

  #   logger.debug( 'id, `%s`; currentlyActiveService is: `%s`; requestSuccessStatus is: `%s`' % (eb_request_number, itemInstance.currentlyActiveService, itemInstance.requestSuccessStatus) )

  #   if ( itemInstance.currentlyActiveService == 'inRhode' ):
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `inRhode`' % eb_request_number )
  #     message = self.prepFirstEmailMessage_InRhode( itemInstance )

  #   elif( itemInstance.currentlyActiveService == 'borrowDirect' ):
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `borrowDirect`' % eb_request_number )
  #     message = self.prepFirstEmailMessage_BorrowDirect( itemInstance )

  #   elif( itemInstance.currentlyActiveService == 'virtualCatalog' ):
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `virtualCatalog`' % eb_request_number )
  #     message = self.prepFirstEmailMessage_VirtualCatalog( itemInstance )

  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'success' ):
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `success`' % eb_request_number )
  #     try:
  #       message = self.prepFirstEmailMessage_Illiad_success( itemInstance )
  #       logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `success`; message is, ```%s```' % (eb_request_number, message) )
  #     except Exception, e:
  #       web_logger.post_message( message='- in classes.UtilityCode.sendEmail(); error, ```%s```' % unicode(repr(e)), identifier=eb_request_number, importance='error' )

  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'illiad_new_user' ):
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `illiad_new_user`' % eb_request_number )
  #     message = self.prepFirstEmailMessage_Illiad_illiadNewUser( itemInstance )
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `illiad_new_user`; new-user message composed' % eb_request_number )

  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'create_illiad_user_failed' ):
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `create_illiad_user_failed`' % eb_request_number )
  #     message = self.prepFirstEmailMessage_Illiad_createIlliadUserFailed( itemInstance )
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `create_illiad_user_failed`; failed message composed' % eb_request_number )

  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'login_failed_possibly_blocked' ):
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `login_failed_possibly_blocked`' % eb_request_number )
  #     message = self.prepFirstEmailMessage_Illiad_loginFailedPossiblyBlocked( itemInstance )
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `login_failed_possibly_blocked`; blocked message composed' % eb_request_number )

  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'failure_no_sfx-link_to_illiad' ):
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `failure_no_sfx-link_to_illiad`' % eb_request_number )
  #     message = self.prepFirstEmailMessage_Illiad_failureNoSfxLinkToIlliad( itemInstance )
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `failure_no_sfx-link_to_illiad`; failed message composed' % eb_request_number )

  #   elif( itemInstance.currentlyActiveService == 'illiad' and itemInstance.requestSuccessStatus == 'illiad_unknown_failure' ):
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `illiad_unknown_failure`' % eb_request_number )
  #     message = self.prepFirstEmailMessage_Illiad_illiadUnknownFailure( itemInstance )
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad` and requestSuccessStatus is `illiad_unknown_failure`; unknown failure message composed' % eb_request_number )

  #   else:
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad`; default unhandled situation`' % eb_request_number )
  #     message = '''BJD - handle this situation.'''
  #     logger.debug( 'id, `%s`; in if currentlyActiveService is `illiad`; default unhandled situation message composed' % eb_request_number )

  #     # end of message-body if statements

  #   ## complete message ##

  #   fullMessage = headerInfo + "\n" + message
  #   logger.debug( 'id, `%s`; fullMessage prepared' % eb_request_number )
  #   fullMessage = fullMessage.encode( 'utf-8', 'ignore' )

  #   ## non-display info -- NOTE: this really controls who it goes to, not the 'To:' info above. ##

  #   sender = ADMIN_EMAIL
  #   try:
  #     recipientList = self.prepFirstEmailRecipientList( itemInstance, eb_request_number )
  #   except Exception, e:
  #     web_logger.post_message( message='- in classes.UtilityCode.sendEmail(); error preparing recipientList, ```%s```' % unicode(repr(e)), identifier=eb_request_number, importance='error' )

  #   logger.debug( 'id, `%s`; sender and recipientList prepared' % eb_request_number )

  #   ## try the send ##

  #   returnValue = "init"
  #   try:
  #     logger.debug( 'id, `%s`; email attempt starting' % eb_request_number )
  #     smtpResult = mailSession.sendmail(sender, recipientList, fullMessage)
  #     logger.debug( 'id, `%s`; email sent successfully' % eb_request_number )
  #     returnValue = 'success' # tentatively
  #   except Exception as e:
  #     mailSession.quit()
  #     logger.error( 'id, `%s`; attempt to send email failed with error, ```%s```' % (eb_request_number, unicode(repr(e))) )
  #     try:
  #       time.sleep(5) # 5 seconds of peace to recharge karma
  #       logger.debug( 'id, `%s`; second email attempt starting' % eb_request_number )
  #       mailSession2 = smtplib.SMTP(smtpServer)
  #       smtpResult2 = mailSession2.sendmail(sender, recipientList, fullMessage)
  #       logger.error( 'id, `%s`; second email sent successfully' % eb_request_number )
  #     except Exception as e:
  #       logger.error( 'id, `%s`; sencond attempt to send email failed with error, ```%s```' % (eb_request_number, unicode(repr(e))) )
  #       mailSession2.quit()
  #       returnValue = 'failure'
  #     else:
  #       mailSession2.quit()
  #       returnValue = "success"
  #       logger.debug( 'id, `%s`; second mail session quit normally' % eb_request_number )
  #   else:
  #     mailSession.quit()
  #     logger.debug( 'id, `%s`; mailSession1 quit normally' % eb_request_number )

  #   return returnValue

  #   # end function sendEmail



# bottom
