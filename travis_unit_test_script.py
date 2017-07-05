import sys
import unittest

from testing_suite.utilities import get_tests_in_this_dir

testsuite = get_tests_in_this_dir('testing_suite')
runner = unittest.TextTestRunner(verbosity=1).run(testsuite)
sys.exit(len(runner.failures) + len(runner.errors))
