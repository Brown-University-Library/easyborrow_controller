"""
- Test class for class UtilityCode.
- Part of easyBorrow python code.
"""


import os, sys, unittest
from easyborrow_controller_code.classes import UtilityCode



class UtilityCodeTest(unittest.TestCase):


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
