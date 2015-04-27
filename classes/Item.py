# get the project's enclosing directory
import json, os, sys
current_script_name = sys.argv[0] # may or may not include path
directory_path = os.path.dirname( current_script_name )
full_directory_path = os.path.abspath( directory_path )
directory_list = full_directory_path.split('/')
last_element_string = directory_list[-2] + '/' + directory_list[-1]
enclosing_directory = full_directory_path.replace( '/' + last_element_string, '' ) # strip off the slash plus the current directory
# print '\n- enclosing_directory is: %s' % enclosing_directory
sys.path.append( enclosing_directory )
import easyborrow_controller_code.settings
sys.path.append( easyborrow_controller_code.settings.INRHODE_TUNNELER_ENCLOSING_DIRECTORY_PATH )



class Item:

  # from db
  itemDbId = ""
  itemTitle = ""
  itemIsbn = ""
  eppn = ""
  patronName = ""
  patronBarcode = ""
  patronEmail = ""
  patronStatus = ""
  patronId = ''
  requestNumber = ""
  sfxurl = ""
  openurl = ""
  firstname = ''
  lastname = ''
  phone = '123-4567' # not yet saved to db
  address = 'address_here' # not yet saved to db
  timePreference = "" # quick or long
  locationPreference = "" # rock or sci
  alternateEditionPreference = "" # y or n
  volumesPreference = "" # varchar(30) field

  # from returned xml
  borrowDirectAssignedUserEmail = ""
  borrowDirectAssignedReferenceNumber = ""
  virtualCatalogAssignedUserEmail = ""
  virtualCatalogAssignedReferenceNumber = ""
  illiadAssignedReferenceNumber = ''
  illiadAssignedSfxUrl = ''
  illiadAssignedAuthId = ''

  # from internal calculations
  illiadTinySfxUrl = ''
  genericAssignedUserEmail = ""
  genericAssignedReferenceNumber = ""
  currentlyActiveService = "" # controller flag property, so when success hits, I know which properties to use for the email.
  requestSuccessStatus = ""
  illiadUrl = ""
  oclcNumber = ''
  patron_api_home_libr = ''
  patron_api_address = ''
  patron_api_telephone = ''
  patron_api_dept = ''
  patron_api_pcode3 = ''



  def constructPasswordHolderUrl( self ):
    '''
    Seems unnecessary, but I was having problems figuring out why the construction of the url was failing; tests above helped.
    '''
    import urllib
    url = '''TODO - delete this function''' % (self.itemDbId, urllib.quote(self.firstname), urllib.quote(self.lastname), urllib.quote(self.patronEmail), urllib.quote(self.patron_api_telephone), urllib.quote(self.patron_api_address), urllib.quote(self.patron_api_pcode3), urllib.quote(self.patron_api_dept) )
    return url



  def filterEmail( self, email_string ):
    new_string = email_string.replace( ' ', '' )
    return new_string



  def createIlliadUserViaPasswordHolder( self, eb_request_number ):

    import sys
    import urllib
    import UtilityCode
    utCdInstance = UtilityCode.UtilityCode()

    # variables in url below should all be filled in from controller call of patron_api and convert_patron_api -- though perhaps that logic should go here.
    utCdInstance.updateLog( message="- In 'Item->createIlliadUserViaPasswordHolder()'; preparing url to 'TODO - delete this old function'", message_importance='high', identifier=eb_request_number )
    url = self.constructPasswordHolderUrl() # broke this simple step out as part of troubleshooting
    utCdInstance.updateLog( message="- In 'Item->createIlliadUserViaPasswordHolder()'; sent url is: %s" % url, message_importance='high', identifier=eb_request_number )

    try:
      create_illiad_user_result = urllib.urlopen(url).read()
      utCdInstance.updateLog( message="- In 'Item->createIlliadUserViaPasswordHolder()'; create_illiad_user_result is: %s" % create_illiad_user_result, message_importance='high', identifier=eb_request_number )
    except:
      create_illiad_user_result = 'unable_to_call_create_illiad_user_service'
      utCdInstance.updateLog( message="- In 'Item->createIlliadUserViaPasswordHolder()'; passwordHolder GET didn\'t go through", message_importance='high', identifier=eb_request_number )

    return create_illiad_user_result



  def encodeTextForUrl(self, keyText, valueText):

    import urllib

    dataDict = {}
    dataDict[keyText] = valueText

    encodedString = urllib.urlencode(dataDict)

    return encodedString



  def updateHistoryReferenceNumber(self, number):
    import UtilityCode

    SQL_PATTERN = unicode( os.environ[u'ezbCTL__INSERT_HISTORY_REFERENCENUM_SQL_PATTERN'] )
    sql = SQL_PATTERN % ( self.itemDbId, number )

    utCdInstance = UtilityCode.UtilityCode()
    utCdInstance.connectExecute(sql)



  def grabConvertedPatronApiInfo( self, patronApiInfo ):


    import UtilityCode
    utCdInstance = UtilityCode.UtilityCode()


    try:

      import Prefs
      prefs_instance = Prefs.Prefs()

      import sys
      # utCdInstance.updateLog( message="- in controller.Item.grabConvertedPatronApiInfo(); sys.path is: %s" % sys.path, message_importance='high', identifier='NA' )
      # sys.path.append( prefs_instance.SIMPLEJSON_ENCLOSING_FOLDER )
      # sys.path.append( './../lib')
      # utCdInstance.updateLog( message="- in controller.Item.grabConvertedPatronApiInfo(); sys.path is now: %s" % sys.path, message_importance='high', identifier='NA' )

      # from django.utils import simplejson
      import urllib

      dataDict = {}
      dataDict['patron_info'] = '''%s''' % (patronApiInfo,)
      encodedString = urllib.urlencode(dataDict)

      url_root = unicode( os.environ[u'ezbCTL__PATRON_API_CONVERTER_URL'] )
      url = u'%s?%s' % ( url_root, encodedString )

      # print '\n- url is: %s' % url
  #   data = urllib.urlopen(url).read()
      data = json.load( urllib.urlopen(url) )
      utCdInstance.updateLog( message="- in controller.Item.grabConvertedPatronApiInfo(); data is: %s" % data, message_importance='high', identifier='NA' )

  #   print '''data is: %s''' % (data,)

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

    import urllib
    if( id == None ):
      id = self.patronId # allows for testing
    url = '%s%s/dump' % ( easyborrow_controller_code.settings.PATRON_API_URL_ROOT, id, )
    data = urllib.urlopen(url).read()

    return data



  def parsePatronApiInfo(self, patronApiString):
    return 'blah'



  ## function not used
  # def makeTinyUrl(self, urlToConvert):
  #
  #   import urllib
  #
  #   baseUrl = 'http://tinyurl.com/api-create.php?url='
  #   fullUrl = baseUrl + urlToConvert
  #   data = urllib.urlopen(fullUrl).read()
  #   return data



  def convertSfxurlToOpenurlSegment(self, sfxurl):

    import urllib

    segmentWithoutPrefix = sfxurl[36:]

    dataDict = {}
    dataDict['openurl'] = '''%s''' % (segmentWithoutPrefix,)

    encodedString = urllib.urlencode(dataDict)

    return encodedString



  # def parseIlliadResultData(self, illiadDataString):
  #
  #   from xml.dom import minidom
  #   import urllib
  #
  #   illiadXmlDoc = minidom.parseString(illiadDataString)
  #
  #   statusElements = illiadXmlDoc.getElementsByTagName('status')
  #   status = statusElements[0].firstChild.data
  #
  #   self.illiadAssignedUserEmail = self.patronEmail
  #
  #   referenceNumberElements = illiadXmlDoc.getElementsByTagName('transaction_number')
  #   if( referenceNumberElements != [] ):
  #     self.illiadAssignedReferenceNumber = referenceNumberElements[0].firstChild.data
  #
  #   sfxUrlElements = illiadXmlDoc.getElementsByTagName('sfx_url')
  #   if( sfxUrlElements != [] ):
  #     initialUrl = sfxUrlElements[0].firstChild.data
  #     decodedUrl = urllib.unquote(initialUrl)
  #     self.illiadAssignedSfxUrl = decodedUrl
  #
  #   authIdElements = illiadXmlDoc.getElementsByTagName('authId')
  #   if( authIdElements != [] ):
  #     self.illiadAssignedAuthId = authIdElements[0].firstChild.data
  #
  #   return status



  def parseIlliadResultData(self, illiadDataString):

    from xml.dom import minidom
    import urllib

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

    import sys
    import urllib
    import UtilityCode
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

    from xml.dom import minidom
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

    import urllib
    virtualCatalogUrl = "TODO - delete this old function" % (self.patronBarcode, self.itemIsbn,)
    virtualCatalogResultData = urllib.urlopen(virtualCatalogUrl).read()

    return virtualCatalogResultData



  def updateHistoryAction(self, serviceName, action, result, number):

    import UtilityCode

    SQL_PATTERN = unicode( os.environ[u'ezbCTL__INSERT_HISTORY_FULLACTION_SQL_PATTERN'] )
    sql = SQL_PATTERN % ( self.itemDbId, serviceName, action, result, number )

    utCdInstance = UtilityCode.UtilityCode()
    recordId = utCdInstance.connectExecute(sql)

    return recordId



  def parseBorrowDirectResultData( self, borrowDirectDataString, eb_request_number ):
    '''
    - Purpose: parse returned api data
    - Called by: controller
    '''

    import UtilityCode
    utCdInstance = UtilityCode.UtilityCode()  # for logging

    import Prefs
    prefs_instance = Prefs.Prefs()

    try:
      utCdInstance.updateLog( message='- in controller.Item.parseBorrowDirectResultData(); about to parse returned bd_data, which is: %s' % borrowDirectDataString, message_importance='high', identifier=eb_request_number )
      data = json.loads( borrowDirectDataString )
      status = data['response']['search_result']
      if status == 'SUCCESS':
        status = 'Request_Successful'  # for logic of calling code
      borrowdirect_email = ''  # not captured by borrowdirect-api; would update self.borrowDirectAssignedUserEmail
      self.borrowDirectAssignedReferenceNumber = data['response']['bd_confirmation_code']
      # borrowdirect_reference_number = ''  # not captured by borrowdirect-api; would update self.borrowDirectAssignedReferenceNumber
      utCdInstance.updateLog( message='- in controller.Item.parseBorrowDirectResultData(); status is: %s' % status, message_importance='high', identifier=eb_request_number )
      return status
    except Exception, e:
      utCdInstance.updateLog( message='- in controller.Item.parseBorrowDirectResultData(); Exception is: %s' % e.__dict__, message_importance='high', identifier=eb_request_number )
      return 'FAILURE'



  def checkBorrowDirect( self, eb_request_number ):
    '''
    - Purpose: hit new (2010-August) borrow-direct web-services
    - Called by: controller
    '''

    import sys, urllib, urllib2
    import UtilityCode


    try:

      utCdInstance = UtilityCode.UtilityCode()  # for logging

      url = easyborrow_controller_code.settings.BD_API_URL

      values_dict = {
      'api_authorization_code': easyborrow_controller_code.settings.BD_API_AUTHORIZATION_CODE,
      'api_identity': easyborrow_controller_code.settings.BD_API_IDENTITY,
      'university': easyborrow_controller_code.settings.BD_UNIVERSITY,
      'user_barcode': self.patronBarcode,
      'isbn': self.itemIsbn,
      'command': 'request',
      }

      utCdInstance.updateLog( message='- in controller.Item.checkBorrowDirect(); about to access BD-API at url %s' % url, message_importance='high', identifier=eb_request_number )
      data = urllib.urlencode( values_dict )
      utCdInstance.updateLog( message='- in controller.Item.checkBorrowDirect(); sending data: %s' % data, message_importance='high', identifier=eb_request_number )
      request = urllib2.Request( url, data )
      response = urllib2.urlopen( request )
      return_val = response.read()
      return return_val  # this will be json

    except Exception, e:
      utCdInstance.updateLog( message='- in controller.Item.checkBorrowDirect(); Exception is: %s' % e.__dict__, message_importance='high', identifier=eb_request_number )
      return 'FAILURE'

    # end def checkBorrowDirect()



  def checkInRhode(self, eb_request_number):

    import sys
    import UtilityCode

    try:
      utCdInstance = UtilityCode.UtilityCode()
      from inrhode_tunneler.inrhode_controller import InRhodeController
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

    import UtilityCode

    SQL_PATTERN = unicode( os.environ[u'ezbCTL__UPDATE_REQUEST_STATUS_SQL_PATTERN'] )
    sql = SQL_PATTERN % ( newStatus, self.itemDbId )

    utCdInstance = UtilityCode.UtilityCode()
    utCdInstance.connectExecute(sql)



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


  def determineFlow(self):
    if len( self.volumesPreference ) > 0:
      flow = [u'illiad']
    elif len( self.itemIsbn ) > 0:
      flow = [ u'bd', u'illiad' ] # changed on 2015-04-27 at request of BB email
      # flow = [ u'bd', u'ir', u'illiad' ] # changed on 2012-09-05 at request of BH from 2012-04-02 email
    else:
      flow = [ u'bd', u'illiad' ]
    return flow


  # def determineFlow(self):
  #
  #   if(self.timePreference == "quick"):
  #
  #     # isbn=yes & volumes=yes
  #     if( self.itemIsbn != "" and self.volumesPreference != "" ):
  #       flow = ['illiad']
  #     # isbn=yes & volumes=no
  #     elif( self.itemIsbn != "" and self.volumesPreference == "" ):
  #       flow = [ 'bd', 'ir', 'illiad' ] # changed on 2012-09-05 at request of BH from 2012-04-02 email
  #       # flow = [ 'ir', 'bd', 'illiad' ] # changed at requst of BB from HH on 2009-01-12-Mon
  #       # flow = [ 'bd', 'ir', 'illiad' ] # changed at requst of BH on 2009-01-06-Tue
  #       # flow = [ 'bd', 'ir', 'vc', 'illiad' ] # changed at requst of HH on 2008-10-27-Mon
  #       # flow = ['ir', 'bd', 'vc', 'illiad']
  #
  #     # isbn=no & volumes=yes
  #     elif( self.itemIsbn == "" and self.volumesPreference != "" ):
  #       flow = ['illiad']
  #     # isbn=no & volumes=no
  #     elif( self.itemIsbn == "" or self.volumesPreference == "" ):
  #       flow = [ u'bd', u'illiad']
  #
  #     # shouldn't get here
  #     else:
  #       flow = ['illiad']
  #
  #   else:
  #
  #     # isbn=yes & volumes=yes
  #     if( self.itemIsbn != "" and self.volumesPreference != "" ):
  #       flow = ['illiad']
  #     # isbn=yes & volumes=no
  #     elif( self.itemIsbn != "" and self.volumesPreference == "" ):
  #       flow = [ u'bd', u'ir', u'illiad']
  #
  #     # isbn=no & volumes=yes
  #     elif( self.itemIsbn == "" and self.volumesPreference != "" ):
  #       flow = ['illiad']
  #     # isbn=no & volumes=no
  #     elif( self.itemIsbn == "" or self.volumesPreference == "" ):
  #       flow = [ u'bd', u'illiad']
  #
  #     # shouldn't get here
  #     else:
  #       flow = ['illiad']
  #
  #   return flow



  def updateHistoryNote(self, note):
    import UtilityCode

    # sql = "INSERT INTO history ( request_id, note ) VALUES ( '%s', '%s' )" % ( self.itemDbId, note )
    SQL_PATTERN = unicode( os.environ[u'ezbCTL__INSERT_HISTORY_NOTE_SQL_PATTERN'] )
    sql = SQL_PATTERN % ( self.itemDbId, note )

    utCdInstance = UtilityCode.UtilityCode()
    utCdInstance.connectExecute(sql)



##
## to run doctests

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
