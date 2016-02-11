# -*- coding: utf-8 -*-

from __future__ import unicode_literals


if __name__ == "__main__":
  ## add project directory to path
  import os, sys, unittest
  current_script_name = sys.argv[0] # may or may not include path
  directory_path = os.path.dirname( current_script_name )
  full_directory_path = os.path.abspath( directory_path )
  directory_list = full_directory_path.split('/')
  path = '/'.join( directory_list[0:-2] )
  sys.path.append( path )

  ## module imports
  # from easyborrow_controller_code.classes import Item, UtilityCode

  ## test imports
  # from easyborrow_controller_code.tests.ItemTest import *
  from easyborrow_controller_code.tests.utility_code_file_tests import *
  # from easyborrow_controller_code.tests.UtilityCodeClassTest import *
  from easyborrow_controller_code.tests.tunneler_runner_tests import *

  unittest.main()
