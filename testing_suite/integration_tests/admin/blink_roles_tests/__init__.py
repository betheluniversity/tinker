import unittest

from testing_suite.integration_tests.unit_test_utilities import get_tests_in_this_dir

if __name__ == "__main__":
    testsuite = get_tests_in_this_dir('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
