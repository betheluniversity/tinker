import sys
# import time
import unittest

from testing_suite.utilities import get_tests_in_this_dir

all_tests = get_tests_in_this_dir('testing_suite')
results = unittest.TextTestRunner(verbosity=1).run(all_tests)

# # Check if any of the errors are from Cascade calls that timed out
# rerun_tests = False
# if len(results.errors) > 0:
#     for err in results.errors:
#         error_message = err[1]
#         if 'Error' in error_message:
#             # Only need to catch the first Cascade timeout error to know that the tests need to be rerun
#             rerun_tests = False  # True
#             break
#
# # This is only true if there was a Cascade timeout error
# if rerun_tests:
#     # Sleep 30 seconds to let Cascade cool off and get ready to receive requests again
#     time.sleep(30)
#     # Rerun the testing suite once
#     # all_tests = get_tests_in_this_dir(".")
#     results = unittest.TextTestRunner(verbosity=1).run(all_tests)

sys.exit(len(results.failures) + len(results.errors))
