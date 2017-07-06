import sys
import unittest

from testing_suite.utilities import get_tests_in_this_dir


# Run unit tests first
print 'UNIT TESTS\n'
unit_tests = get_tests_in_this_dir('testing_suite/unit_tests')
unit_tests_run = unittest.TextTestRunner(verbosity=1).run(unit_tests)

# Run integration tests second
print 'INTEGRATION TESTS\n'
integration_tests = get_tests_in_this_dir('testing_suite/integration_tests')
integration_tests_run = unittest.TextTestRunner(verbosity=1).run(integration_tests)

sys.exit(len(unit_tests_run.failures) + len(unit_tests_run.errors) +
         len(integration_tests_run.failures) + len(integration_tests_run.errors))
