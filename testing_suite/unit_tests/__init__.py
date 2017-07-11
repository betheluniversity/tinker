import unittest

from testing_suite import BaseTestCase
from testing_suite.utilities import get_tests_in_this_dir
from tinker import app


class UnitTestCase(BaseTestCase):
    def __init__(self, methodName):
        super(UnitTestCase, self).__init__(methodName)

    def setUp(self):
        app.config['UNIT_TESTING'] = True

    def generate_failure_message(self, class_name, line_number):
        # Usage: self.assertTrue(<some boolean expression>,
        #                        msg=self.generate_failure_message(self.class_name, self.get_line_number())
        return '%(0)s failed on line %(1)s.' % {'0': class_name, '1': line_number}

    def tearDown(self):
        app.config['UNIT_TESTING'] = False

if __name__ == "__main__":
    testsuite = get_tests_in_this_dir('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
