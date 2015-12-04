# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
- Test class for class Item.
- Part of easyBorrow python code.
"""

import os, sys, unittest
from easyborrow_controller_code import settings
from easyborrow_controller_code.classes import UtilityCode



class ItemTest(unittest.TestCase):



  def testGrabConvertedPatronApiInfo(self):

    # check name directly from data
    item_instance = Item.Item()
    patron_api_info = item_instance.grabPatronApiInfo( settings.TEST_PATRON_04_ID )
    data = item_instance.grabConvertedPatronApiInfo( patron_api_info )
    result = data[ 'PATRNNAME' ]
    assert result == settings.TEST_PATRON_04_CONVERTED_PATRNNAME, result

    ## check item_instance properties

    # address
    result = item_instance.patron_api_address
    assert result == settings.TEST_PATRON_04_CONVERTED_ADDRESS, result

    # phone
    result = item_instance.patron_api_telephone
    assert result == settings.TEST_PATRON_04_CONVERTED_PHONE, result

    # department
    expected = settings.TEST_PATRON_04_CONVERTED_DEPARTMENT
    result = item_instance.patron_api_dept
    self.assertTrue( expected == result, '\nExpected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

    # another patron's phone
    item_instance = Item.Item()
    patron_api_info = item_instance.grabPatronApiInfo( settings.TEST_PATRON_05_ID )
    data = item_instance.grabConvertedPatronApiInfo( patron_api_info )
    expected = settings.TEST_PATRON_05_CONVERTED_PHONE
    result = item_instance.patron_api_telephone
    self.assertTrue( expected == result, '\nExpected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

    # another patron's status
    item_instance = Item.Item()
    patron_api_info = item_instance.grabPatronApiInfo( settings.TEST_PATRON_02_ID )
    data = item_instance.grabConvertedPatronApiInfo( patron_api_info )
    expected = settings.TEST_PATRON_02_CONVERTED_STATUS
    result = item_instance.patron_api_pcode3
    self.assertTrue( expected == result, '\nExpected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

    ## check bad patronApi data conversion

    # bad email address (has a space in the middle!)
    item_instance = Item.Item()
    patron_api_data = item_instance.grabPatronApiInfo( settings.TEST_PATRON_01_ID )
    converted_patron_api_data = item_instance.grabConvertedPatronApiInfo( patron_api_data )
    expected = settings.TEST_PATRON_01_CONVERTED_EMAIL
    result = item_instance.patronEmail
    self.assertTrue( expected == result, '\nExpected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

    # end def testGrabConvertedPatronApiInfo()



  def testGrabPatronApiInfo(self):
    itemInstance = Item.Item()
    needleText = 'TODO - add test env-var'
    haystackText = itemInstance.grabPatronApiInfo( settings.TEST_PATRON_ID )
    expected = True
    result = haystackText.find(needleText) > -1
    self.assertEqual(expected, result, "result is: " + str(result))



  # def testCheckIlliad_forUrl(self):

  #   itemInstance = Item.Item()
  #   itemInstance.itemDbId = '123'
  #   itemInstance.sfxurl = 'TODO - add test env-var'
  #   itemInstance.firstname = 'TODO - add test env-var'
  #   itemInstance.lastname = 'TODO - add test env-var'
  #   itemInstance.patronEmail = 'TODO - add test env-var'
  #   itemInstance.patronStatus = 'undergraduate'
  #   itemInstance.volumesPreference = 'Volumes 2 - 5'
  #   itemInstance.oclcNumber = '1234'
  #   eb_request_number = 'test-case test-request-number'
  #   try:
  #     itemInstance.checkIlliad( eb_request_number )
  #     expected = '''TODO - add test env-var'''
  #     result = itemInstance.illiadUrl
  #     self.assertEqual(expected, result, "result is: " + str(result))
  #   except:
  #     expected = '''TODO - add test env-var'''
  #     result = itemInstance.illiadUrl
  #     self.assertTrue( expected == result, '\nExpected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

  #   # end def testCheckIlliad_forUrl()



  def testConvertSfxurlToOpenurlSegment(self):

    itemInstance = Item.Item()
    sfxurl = '''http://url_root?sid=FirstSearch%3AWorldCat&genre=book&isbn=9781591144038&title=Jack%20Aubrey%20commands%20%3A%20an%20historical%20companion%20to%20the%20naval%20world%20of%20Patrick%20O%27Brian%20%20&aulast=Lavery&aufirst=Brian&id=doi%'''

    expected = '''openurl=sid%3DFirstSearch%253AWorldCat%26genre%3Dbook%26isbn%3D9781591144038%26title%3DJack%2520Aubrey%2520commands%2520%253A%2520an%2520historical%2520companion%2520to%2520the%2520naval%2520world%2520of%2520Patrick%2520O%2527Brian%2520%2520%26aulast%3DLavery%26aufirst%3DBrian%26id%3Ddoi%25'''
    result = itemInstance.convertSfxurlToOpenurlSegment(sfxurl)
    self.assertEqual(expected, result, "result is: " + str(result))



  def testParseIlliadResultData_newUser(self):

    itemInstance = Item.Item()

    resultData = '''<?xml version="1.0" ?>

<illiad_webservice_result>
  <submitted_parameters>
    <key>151</key>
    <service>illiad</service>
  </submitted_parameters>
  <result>
    <status>login_failed_new_user</status>
    <sfx_url>TODO - add test env-var</sfx_url>
  </result>
  <info>
    A project of the Brown University Library. Contact: 'TODO - add test env-var'.
  </info>
</illiad_webservice_result>'''

    expected = "login_failed_new_user"
    result = itemInstance.parseIlliadResultData(resultData)
    self.assertEqual(expected, result, "result is: " + str(result))

    expected = "TODO - replace string with env var if needed"
    result = itemInstance.illiadAssignedSfxUrl
    self.assertEqual(expected, result, "result is: " + str(result))



  def testParseIlliadResultData_requestSuccessful(self):

    itemInstance = Item.Item()

    ###
    # Happy path -- request successful
    ###

    resultData = '''<?xml version="1.0" ?>

<illiad_webservice_result>
  <submitted_parameters>
    <key>123</key>
    <openurl>zzz</openurl>

    <service>illiad</service>
  </submitted_parameters>
  <result>
    <status>submission_successful</status>
    <transaction_number>263516</transaction_number>
  </result>
  <info>

    A project of the Brown University Library. Contact: 'TODO - add test env-var'.
  </info>
</illiad_webservice_result>'''

    expected = "submission_successful"
    result = itemInstance.parseIlliadResultData(resultData)
    self.assertEqual(expected, result, "result is: " + str(result))

    expected = "263516"
    result = itemInstance.illiadAssignedReferenceNumber
    self.assertEqual(expected, result, "result is: " + str(result))



  def testParseIlliadResultData_no_login_data(self):

    itemInstance = Item.Item()

    resultData = '''<?xml version="1.0" ?>

<message>no_login_data_available</message>'''

    expected = "no_login_data_available"
    result = itemInstance.parseIlliadResultData(resultData)
    self.assertEqual(expected, result, "result is: " + str(result))



  # def testUpdateHistoryWithStart(self):

  #   # from easyborrow_controller_code.classes import UtilityCode

  #   itemInstance = Item.Item()
  #   utCdInstance = UtilityCode.UtilityCode()
  #   itemInstance.itemDbId = 999999999
  #   historyNoteParameter = "test entry abc123"
  #   itemInstance.updateHistoryNote( historyNoteParameter )

  #   expected = "test entry abc123"

  #   sql = 'TODO - add test env var'
  #   resultInfo = utCdInstance.connectExecuteSelect(sql) # [ [fieldname01, fieldname02], ( (row01field01_value, row01field02_value), (row02field01_value, row02field02_value) ) ]

  #   fieldNameList = resultInfo[0]
  #   allRowsTuple = resultInfo[1] # all rows

  #   rowTuple = allRowsTuple[0] # first row

  #   result = rowTuple[ fieldNameList.index('note') ] # 'note' field

  #   self.assertEqual(expected, result, "result is: " + str(result))

  #   # clean up - delete test record

  #   sql = "DELETE FROM  history WHERE  history.request_id = 999999999"
  #   utCdInstance.connectExecute(sql)



if __name__ == "__main__":
  ## get the project's enclosing directory for import references
  current_script_name = sys.argv[0] # may or may not include path
  directory_path = os.path.dirname( current_script_name )
  full_directory_path = os.path.abspath( directory_path )
  directory_list = full_directory_path.split('/')
  last_element_string = directory_list[-2] + '/' + directory_list[-1]
  enclosing_directory = full_directory_path.replace( '/' + last_element_string, '' ) # strip off the slash plus the current directory
  sys.path.append( enclosing_directory )
  ## ok, rest of imports
  from easyborrow_controller_code import settings
  from easyborrow_controller_code.classes import Item

  unittest.main()



# bottom
