import os
import unittest
from inspect import stack, getframeinfo

from testing_suite.utilities import get_tests_in_this_dir
from tinker import app


class BaseUnitTestCase(unittest.TestCase):
    def __init__(self, methodName):
        super(BaseUnitTestCase, self).__init__(methodName)
        current_frame = stack()[1]
        file_of_current_frame = current_frame[0].f_globals.get('__file__', None)
        dir_path_to_current_frame = os.path.dirname(file_of_current_frame)
        name_of_last_folder = dir_path_to_current_frame.split("/")[-1]
        self.class_name = name_of_last_folder + "/" + self.__class__.__name__

    def setUp(self):
        app.config['UNIT_TESTING'] = True

    def get_line_number(self):
        current_frame = stack()[1][0]
        frameinfo = getframeinfo(current_frame)
        return frameinfo.lineno

    def generate_failure_message(self, class_name, line_number):
        # Usage: self.assertTrue(<some boolean expression>,
        #                        msg=self.generate_failure_message(self.class_name, self.get_line_number())
        return '%(0)s failed on line %(1)s.' % {'0': class_name, '1': line_number}

    def assertIn(self, substring, string_to_check, msg=None):
        self.failIf(substring not in string_to_check, msg=msg)

    def assertNotIn(self, substring, string_to_check, msg=None):
        self.failIf(substring in string_to_check, msg=msg)

    def tearDown(self):
        app.config['UNIT_TESTING'] = False

if __name__ == "__main__":
    testsuite = get_tests_in_this_dir('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
