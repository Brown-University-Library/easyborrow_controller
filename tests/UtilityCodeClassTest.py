"""
- Test class for class UtilityCode.
- Part of easyBorrow python code.
"""


import os, sys, unittest
from easyborrow_controller_code.classes import UtilityCode



class UtilityCodeTest(unittest.TestCase):



  #-> commented out because I haven't yet been replicated the error
  # def test_prepFirstEmailMessage_Illiad_success(self):
  #   '''
  #   - Purpose: to test unicode issue.
  #   '''
  #
  #   from classes import Item
  #   i = Item.Item()
  #   i.firstname = 'first'
  #   i.lastname = 'last'
  #   i.itemTitle = 'Zen und die Kunst, ein Motorrad zu warten : ein Versuch \xc3\xbcber Werte'
  #   i.itemTitle = 'Zen und die Kunst, ein Motorrad zu warten : ein Versuch \xc3\xbcber Werte'
  #   i.requestNumber = '123'
  #   i.genericAssignedReferenceNumber = 'test_123'
  #   i.genericAssignedUserEmail = 'a@a.org'
  #   u_instance = UtilityCode.UtilityCode()
  #
  #   expected = 'blah'
  #   result = u_instance.prepFirstEmailMessage_Illiad_success( i )
  #   self.assertTrue( expected == result, '\nExpected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )
  #
  #   # end def test_prepFirstEmailMessage_Illiad_success()


  def test_checkExceptionMessageSyntax(self):
    ucInstance = UtilityCode.UtilityCode()
    result = ucInstance.returnExceptionMessage()
    assert u"error-type - <type 'exceptions.ZeroDivisionError'>; error-message - integer division or modulo by zero; line-number -" in result, result
    # end def test_checkExceptionMessageSyntax()


  def testConnectExecuteSelect(self):

    # empty resultset
    ucInstance = UtilityCode.UtilityCode()
    sql = 'TODO - add test env var'
    expected = None
    result = ucInstance.connectExecuteSelect(sql) # [ [fieldname01, fieldname02], ( (row01field01_value, row01field02_value), (row02field01_value, row02field02_value) ) ]
    self.assertEqual(expected, result, "result is: " + str(result))



  def testUpdateLog(self):

    ucInstance = UtilityCode.UtilityCode()
    message = 'test-case test-message'
    importance = 'high'
    identifier = 'test-case test-identifier'

    expected = 'success'
    result = ucInstance.updateLog( message, importance, identifier )
    self.assertTrue( expected == result, '\nExpected: ->%s<-; \nresult is: ->%s<-' % (expected, result,) )

    # end def testUpdateLog()



  def testObtainDate(self):

    """sending a known time to check formatting"""
    ucInstance = UtilityCode.UtilityCode()
    ucInstance.timeToFormat = (2005, 7, 13, 13, 41, 39, 2, 194, 1) # 'Wed Jul 13 13:41:39 EDT 2005'
    expected = "Wed Jul 13 13:41:39 EDT 2005"
    result = ucInstance.obtainDate()
    self.assertEqual(expected, result, "result is: " + str(result))



# def testSendEmail_newUser(self):
#
#   ucInstance = UtilityCode.UtilityCode()
#   itemInstance = Item.Item()
#
#   # sample patron info
#   itemInstance.itemTitle = '''EMAIL-TEST, NO NEED TO PROCESS --- The Ahwahnee : Yosemite's grand hotel'''
#   itemInstance.itemDbId = '9999 - (not real)'
#   itemInstance.sfxurl = 'http://url_root?sid=FirstSearch%3AWorldCat&genre=book&isbn=9781930238145&title=The%20Ahwahnee%20%3A%20Yosemite%27s%20grand%20hotel%20%20&aulast=Walklet&aufirst=Keith&auinitm=S&id=doi%3A&pid=%3Caccession%20number%3E57248063%3C%2Faccession%20number%3E%3Cfssessid%3Efsapp3-59247-ey1nqcev-donngn%3C%2Ffssessid%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook&req_id=%3Csessionid%3Efsapp3-59247-ey1nqcev-donngn%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E57248063%3C%2Faccessionnumber%3E&rft_ref_fmt=info%3Aofi%2Ffmt%3Axml%3Axsd%3Aoai_dc&rft_ref=http%3A%2F%2Fpartneraccess.oclc.org%2Fwcpa%2Fservlet%2FOUDCXML%3Foclcnum%3D57248063&rft_id=info%3Aoclcnum%2F57248063&rft_id=urn%3AISBN%3A9781930238145&rft.aulast=Walklet&rft.aufirst=Keith&rft.auinitm=S&rft.btitle=The%20Ahwahnee%20%3A%20Yosemite%27s%20grand%20hotel%20%20&rft.isbn=9781930238145&rft.aucorp=Yosemite%20Association.&rft.place=Yosemite%20National%20Park%20%20Calif.&rft.pub=DNC%20Parks%20%26%20Resorts%20at%20Yosemite%20and%20Yosemite%20Association&rft.genre=book'
#   itemInstance.firstname = 'TODO: add test env-var'
#   itemInstance.lastname = 'TODO: add test env-var'
#   itemInstance.patronEmail = 'TODO: add test env-var'
#   itemInstance.patronStatus = 'undergraduate'
#   itemInstance.alternateEditionPreference = "y" # y or n
#   itemInstance.volumesPreference = "" # varchar(30) field
#   itemInstance.patronId = 'TODO: add test env-var'
#   itemInstance.oclcNumber = '57248063'
#   itemInstance.patron_api_address = 'TODO: add test env-var'
#   itemInstance.patron_api_dept = 'UNIV LIBR-WEB SERVICES'
#   itemInstance.patron_api_telephone = 'TODO: add test env-var'
#   itemInstance.patron_api_pcode3 = 'Staff'
#
#   # sample processing info
#   itemInstance.currentlyActiveService = 'illiad'
#   itemInstance.requestSuccessStatus = 'illiad_new_user'
#
#   expected = 'success'
#   result = ucInstance.sendEmail(itemInstance)
#   self.assertEqual(expected, result, "result is: " + str(result))



if __name__ == "__main__":
  ## get the project's enclosing directory for import references
  current_script_name = sys.argv[0] # may or may not include path
  directory_path = os.path.dirname( current_script_name )
  full_directory_path = os.path.abspath( directory_path )
  directory_list = full_directory_path.split('/')
  last_element_string = directory_list[-2] + '/' + directory_list[-1]
  enclosing_directory = full_directory_path.replace( '/' + last_element_string, '' ) # strip off the slash plus the current directory
  # print '\n- enclosing_directory is: %s' % enclosing_directory
  sys.path.append( enclosing_directory )
  ## ok, rest of imports
  from easyborrow_controller_code.classes import UtilityCode

  unittest.main()



# bottom
