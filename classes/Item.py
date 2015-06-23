# -*- coding: utf-8 -*-

import json, os, sys, urllib
from xml.dom import minidom
#
from easyborrow_controller_code import settings
from easyborrow_controller_code.classes import Prefs, UtilityCode
from inrhode_tunneler.inrhode_controller import InRhodeController



class Item( object ):


  def __init__( self ):
    # from db
    self.itemDbId = ""
    self.itemTitle = ""
    self.itemIsbn = ""
    self.eppn = ""
    self.patronName = ""
    self.patronBarcode = ""
    self.patronEmail = ""
    self.patronStatus = ""
    self.patronId = ''
    self.requestNumber = ""
    self.sfxurl = ""
    self.openurl = ""
    self.firstname = ''
    self.lastname = ''
    self.phone = '123-4567' # not yet saved to db
    self.address = 'address_here' # not yet saved to db
    self.timePreference = "" # quick or long
    self.locationPreference = "" # rock or sci
    self.alternateEditionPreference = "" # y or n
    self.volumesPreference = "" # varchar(30) field

    # from returned xml
    self.borrowDirectAssignedUserEmail = ""
    self.borrowDirectAssignedReferenceNumber = ""
    self.virtualCatalogAssignedUserEmail = ""
    self.virtualCatalogAssignedReferenceNumber = ""
    self.illiadAssignedReferenceNumber = ''
    self.illiadAssignedSfxUrl = ''
    self.illiadAssignedAuthId = ''

    # from internal calculations
    self.illiadTinySfxUrl = ''
    self.genericAssignedUserEmail = ""
    self.genericAssignedReferenceNumber = ""
    self.currentlyActiveService = "" # controller flag property, so when success hits, I know which properties to use for the email.
    self.requestSuccessStatus = ""
    self.illiadUrl = ""
    self.oclcNumber = ''
    self.patron_api_home_libr = ''
    self.patron_api_address = ''
    self.patron_api_telephone = ''
    self.patron_api_dept = ''
    self.patron_api_pcode3 = ''


  def constructPasswordHolderUrl( self ):
    '''
    Seems unnecessary, but I was having problems figuring out why the construction of the url was failing; tests above helped.
    '''
    url = '''TODO - delete this function''' % (self.itemDbId, urllib.quote(self.firstname), urllib.quote(self.lastname), urllib.quote(self.patronEmail), urllib.quote(self.patron_api_telephone), urllib.quote(self.patron_api_address), urllib.quote(self.patron_api_pcode3), urllib.quote(self.patron_api_dept) )
    return url


  def filterEmail( self, email_string ):
    new_string = email_string.replace( ' ', '' )
    return new_string


  def encodeTextForUrl(self, keyText, valueText):

    dataDict = {}
    dataDict[keyText] = valueText

    encodedString = urllib.urlencode(dataDict)

    return encodedString


  def updateHistoryReferenceNumber(self, number):

    SQL_PATTERN = unicode( os.environ[u'ezbCTL__INSERT_HISTORY_REFERENCENUM_SQL_PATTERN'] )
    sql = SQL_PATTERN % ( self.itemDbId, number )

    utCdInstance = UtilityCode.UtilityCode()
    utCdInstance.connectExecute(sql)



  def grabConvertedPatronApiInfo( self, patronApiInfo ):

    utCdInstance = UtilityCode.UtilityCode()

    try:

      prefs_instance = Prefs.Prefs()

      dataDict = {}
      dataDict['patron_info'] = '''%s''' % (patronApiInfo,)
      encodedString = urllib.urlencode(dataDict)

      url_root = unicode( os.environ[u'ezbCTL__PATRON_API_CONVERTER_URL'] )
      url = u'%s?%s' % ( url_root, encodedString )

      data = json.load( urllib.urlopen(url) )
      utCdInstance.updateLog( message="- in controller.Item.grabConvertedPatronApiInfo(); data is: %s" % data, message_importance='high', identifier='NA' )

      self.patron_api_address = data['ADDRESS']
      self.patron_api_telephone = data['TELEPHONE']
      utCdInstance.updateLog( message="- in controller.Item.grabConvertedPatronApiInfo(); self.patron_api_telephone is: %s" % self.patron_api_telephone, message_importance='high', identifier='NA' )
      self.patron_api_dept = data['DEPT']
      self.patron_api_pcode3 = data['pcode3_text']

      filtered_patron_email = self.filterEmail( self.patronEmail )

      if ( (filtered_patron_email != None) and (filtered_patron_email != '') ): # regular email good; use it
        self.patronEmail = filtered_patron_email
      else:                                                                     # regular email bad; use net-id
        net_id = data['NET-ID']
        filtered_net_id = self.filterEmail( net_id )
        if( (filtered_net_id != None) and (filtered_net_id != '') ):            # ...if it's good
          self.patronEmail = filtered_net_id
        else:
          self.patronEmail = 'unknown_email'                                    # otherwise hardcode the unknown status

      if( self.patron_api_pcode3 == None ):
        self.patron_api_pcode3 = u'unknown'

      return data

    except Exception, e:

      utCdInstance.updateLog( message="- in controller.Item.grabConvertedPatronApiInfo(); exception is: %s" % e, message_importance='high', identifier='NA' )
      return 'Exception: %s' % e

    # end def grabConvertedPatronApiInfo()


  def grabPatronApiInfo(self, id):

    if( id == None ):
      id = self.patronId # allows for testing
    url = '%s%s/dump' % ( easyborrow_controller_code.settings.PATRON_API_URL_ROOT, id, )
    data = urllib.urlopen(url).read()

    return data


  def parsePatronApiInfo(self, patronApiString):
    return 'blah'


  def convertSfxurlToOpenurlSegment(self, sfxurl):

    segmentWithoutPrefix = sfxurl[36:]

    dataDict = {}
    dataDict['openurl'] = '''%s''' % (segmentWithoutPrefix,)

    encodedString = urllib.urlencode(dataDict)

    return encodedString


  def parseIlliadResultData(self, illiadDataString):

    illiadXmlDoc = minidom.parseString(illiadDataString)

    statusElements = illiadXmlDoc.getElementsByTagName('status')
    try:
      status = statusElements[0].firstChild.data
    except:
      messageElements = illiadXmlDoc.getElementsByTagName('message')
      status = messageElements[0].firstChild.data

    self.illiadAssignedUserEmail = self.patronEmail

    referenceNumberElements = illiadXmlDoc.getElementsByTagName('transaction_number')
    if( referenceNumberElements != [] ):
      self.illiadAssignedReferenceNumber = referenceNumberElements[0].firstChild.data

    sfxUrlElements = illiadXmlDoc.getElementsByTagName('sfx_url')
    if( sfxUrlElements != [] ):
      initialUrl = sfxUrlElements[0].firstChild.data
      decodedUrl = urllib.unquote(initialUrl)
      self.illiadAssignedSfxUrl = decodedUrl

    authIdElements = illiadXmlDoc.getElementsByTagName('authId')
    if( authIdElements != [] ):
      self.illiadAssignedAuthId = authIdElements[0].firstChild.data

    return status


  def checkIlliad( self, eb_request_number ):

    utCdInstance = UtilityCode.UtilityCode()

    # prepare segments
    openurlSegment = self.convertSfxurlToOpenurlSegment(self.sfxurl)
    #
    volumesKeyString = 'volumes'
    volumesValueString = self.volumesPreference
    volumesSegment = self.encodeTextForUrl( volumesKeyString, volumesValueString )

    tempIlliadUrl = '''TODO - delete this old function''' % (self.itemDbId, openurlSegment, urllib.quote(self.firstname), urllib.quote(self.lastname), self.patronEmail, self.patronStatus, volumesSegment, self.oclcNumber )
    self.illiadUrl = tempIlliadUrl # allows testing
    utCdInstance.updateLog( message="- in controller.Item.checkIlliad(); illiadUrl is: %s" % self.illiadUrl, message_importance='low', identifier=eb_request_number )

    try:
      illiadResultData = urllib.urlopen(self.illiadUrl).read()
      utCdInstance.updateLog( message="- in controller.Item.checkIlliad(); illiadResultData is: %s" % illiadResultData, message_importance='low', identifier=eb_request_number )
    except:
      utCdInstance.updateLog( message="- in controller.Item.checkIlliad(); illiad url-request didn\'t go through", message_importance='high', identifier=eb_request_number )

    return illiadResultData


  def parseVirtualCatalogResultData(self, virtualCatalogDataString):

    vcXmlDoc = minidom.parseString(virtualCatalogDataString)

    statusElements = vcXmlDoc.getElementsByTagName('Status')
    if( statusElements[0].firstChild != None ):
      status = statusElements[0].firstChild.data
    else:
      status = 'No_Status_Returned'

    emailElements = vcXmlDoc.getElementsByTagName('AssignedUserEmail')
    if( emailElements != [] ):
      self.virtualCatalogAssignedUserEmail = emailElements[0].firstChild.data

    referenceNumberElements = vcXmlDoc.getElementsByTagName('AssignedRequestId')
    if( referenceNumberElements != [] ):
      self.virtualCatalogAssignedReferenceNumber = referenceNumberElements[0].firstChild.data

    return status


  def checkVirtualCatalog(self):

    virtualCatalogUrl = "TODO - delete this old function" % (self.patronBarcode, self.itemIsbn,)
    virtualCatalogResultData = urllib.urlopen(virtualCatalogUrl).read()

    return virtualCatalogResultData


  def updateHistoryAction(self, serviceName, action, result, number):

    SQL_PATTERN = unicode( os.environ[u'ezbCTL__INSERT_HISTORY_FULLACTION_SQL_PATTERN'] )
    sql = SQL_PATTERN % ( self.itemDbId, serviceName, action, result, number )

    utCdInstance = UtilityCode.UtilityCode()
    recordId = utCdInstance.connectExecute(sql)

    return recordId


  def checkInRhode(self, eb_request_number):

    try:
      utCdInstance = UtilityCode.UtilityCode()
      ir_controller = InRhodeController()
      inRhodeResultData = 'init'
      inRhodeResultData = ir_controller.runCode( self.itemIsbn, self.lastname, self.patronBarcode )
      return inRhodeResultData

    except Exception, e:
      utCdInstance.updateLog(
        message='error-type - %s; error-message - %s; line-number - %s' % ( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno, ),
        # message='In Item.checkInRhode; exception is: %s' % e,
        message_importance='high',
        identifier=eb_request_number )


  def updateRequestStatus(self, newStatus):

    SQL_PATTERN = unicode( os.environ[u'ezbCTL__UPDATE_REQUEST_STATUS_SQL_PATTERN'] )
    sql = SQL_PATTERN % ( newStatus, self.itemDbId )

    utCdInstance = UtilityCode.UtilityCode()
    utCdInstance.connectExecute(sql)


  def fill_from_db_row( self, db_dct ):
    """ Updates attributes from found record data.
        Called by controller.run_code() """
    self.itemDbId = db_dct['id']
    self.requestNumber = db_dct['id']
    self.itemTitle = db_dct['title']
    self.itemIsbn = db_dct['isbn']
    self.timePreference = db_dct['pref']
    self.locationPreference = db_dct['loc']
    self.alternateEditionPreference = db_dct['alt_edition']
    self.volumesPreference = db_dct['volumes']
    self.sfxurl = db_dct['sfxurl']
    self.patronName = db_dct['name']
    self.patronBarcode = db_dct['barcode']
    self.patronEmail = db_dct['email']
    self.patronId = db_dct['patronId']
    tempFirstname = db_dct['firstname']
    self.firstname = tempFirstname.strip()
    tempLastname = db_dct['lastname']
    self.lastname = tempLastname.strip()
    self.patronStatus = db_dct['group'] # for temp ILL staff manual new-user registration
    self.oclcNumber = db_dct['wc_accession'] # for temp ILL staff manual new-user registration
    self.eppn = db_dct['eppn']  # new as of 2012-05
    return


  def fillFromDbRow(self, resultInfo):

    fieldNameList = resultInfo[0]
    allRowsTuple = resultInfo[1]
    rowTuple = allRowsTuple[0] # first row

    self.itemDbId = rowTuple[ fieldNameList.index('id') ]
    self.requestNumber = rowTuple[ fieldNameList.index('id') ]
    self.itemTitle = rowTuple[ fieldNameList.index('title') ]
    self.itemIsbn = rowTuple[ fieldNameList.index('isbn') ]
    self.timePreference = rowTuple[ fieldNameList.index('pref') ]
    self.locationPreference = rowTuple[ fieldNameList.index('loc') ]
    self.alternateEditionPreference = rowTuple[ fieldNameList.index('alt_edition') ]
    self.volumesPreference = rowTuple[ fieldNameList.index('volumes') ]
    self.sfxurl = rowTuple[ fieldNameList.index('sfxurl') ]
    self.patronName = rowTuple[ fieldNameList.index('name') ]
    self.patronBarcode = rowTuple[ fieldNameList.index('barcode') ]
    self.patronEmail = rowTuple[ fieldNameList.index('email') ]
    self.patronId = rowTuple[ fieldNameList.index('patronId') ]
    tempFirstname = rowTuple[ fieldNameList.index('firstname') ]
    self.firstname = tempFirstname.strip()
    tempLastname = rowTuple[ fieldNameList.index('lastname') ]
    self.lastname = tempLastname.strip()
    self.patronStatus = rowTuple[ fieldNameList.index('group') ] # for temp ILL staff manual new-user registration
    self.oclcNumber = rowTuple[ fieldNameList.index('wc_accession') ] # for temp ILL staff manual new-user registration
    self.eppn = rowTuple[ fieldNameList.index('eppn') ]  # new as of 2012-05


  def updateHistoryNote(self, note):

    SQL_PATTERN = unicode( os.environ[u'ezbCTL__INSERT_HISTORY_NOTE_SQL_PATTERN'] )
    sql = SQL_PATTERN % ( self.itemDbId, note )

    utCdInstance = UtilityCode.UtilityCode()
    utCdInstance.connectExecute(sql)


  # end class Item
