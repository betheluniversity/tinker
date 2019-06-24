import unittest

from testing_suite.utilities import get_tests_in_this_dir

# todo: this is repeated in the next folder up's __init__
if __name__ == "__main__":
    testsuite = get_tests_in_this_dir('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)