# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
To test all...
$ python ./test.py

To run specific test...
$ python ./tests/illiad_caller_tests.py IlliadApiRunnerTest.test_make_openurl_segment__simple_case
"""

import logging, os, sys, unittest

## add project parent-directory to sys.path
parent_working_dir = os.path.abspath( os.path.join(os.getcwd(), os.pardir) )
sys.path.append( parent_working_dir )

from easyborrow_controller_code.tests import bd_caller_tests
from easyborrow_controller_code.tests import emailer_tests
from easyborrow_controller_code.tests import illiad_caller_tests


logging.basicConfig(
    filename='',
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
logger = logging.getLogger(__name__)


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest( bd_caller_tests.suite() )  # stub only, TODO make tests
    test_suite.addTest( emailer_tests.suite() )
    test_suite.addTest( illiad_caller_tests.suite() )
    return test_suite


runner = unittest.TextTestRunner()
runner.run( suite() )
