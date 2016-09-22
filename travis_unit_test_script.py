import sys
import unittest
from unit_tests.unit_test_utilities import get_tests_in_this_dir

testsuite = get_tests_in_this_dir('unit_tests')
runner = unittest.TextTestRunner(verbosity=1).run(testsuite)
sys.exit(len(runner.failures) + len(runner.errors))
