# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
To test all...
$ python ./test.py

To run specific test...
$ python ./tests/tunneler_runner_tests.py BDRunnerTest.test_determineSearchType
"""

import logging, unittest
from tests import emailer_tests
from tests import tunneler_runner_tests


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

hndlr = logging.StreamHandler()
hndlr.setLevel( logging.DEBUG )
hndlr.setFormatter( formatter )
logger.addHandler( hndlr )


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest( emailer_tests.suite() )
    test_suite.addTest( tunneler_runner_tests.suite() )
    return test_suite


runner = unittest.TextTestRunner()
runner.run( suite() )
