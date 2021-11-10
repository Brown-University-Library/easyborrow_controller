# if __name__ == "__main__":
#   ## add project directory to path
#   import os, sys, unittest
#   current_script_name = sys.argv[0] # may or may not include path
#   directory_path = os.path.dirname( current_script_name )
#   full_directory_path = os.path.abspath( directory_path )
#   directory_list = full_directory_path.split('/')
#   path = '/'.join( directory_list[0:-2] )
#   sys.path.append( path )

#   ## module imports
#   # from easyborrow_controller_code.classes import Item, UtilityCode

#   ## test imports
#   # from easyborrow_controller_code.tests.ItemTest import *
#   from easyborrow_controller_code.tests.utility_code_file_tests import *
#   # from easyborrow_controller_code.tests.UtilityCodeClassTest import *
#   from easyborrow_controller_code.tests.tunneler_runner_tests import *

#   unittest.main()


# import sys
# if (sys.version_info < (3, 0)):
#     raise Exception( 'python3 or bust' )

# import os
# sys.path.append( os.environ['ezbCTL__ENCLOSING_PROJECT_PATH'] )
