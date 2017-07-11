"""

Extract from https://www.fullstackpython.com/integration-testing.html:

'Integration testing exercises two or more parts of an application at once, including the interactions between the
parts, to determine if they function as intended. This type of testing identifies defects in the interfaces between
disparate parts of a codebase as they invoke each other and pass data between themselves.

While unit testing is used to find bugs in individual functions, integration testing tests the system as a whole.'


Based off of the paradigm described above, the integration_tests folder has tests in it that test connecting to an
endpoint on the tinker webpage and making sure that it returns the correct HTML based off of the parameters passed to
it from the URL args and any POST data it may have. On the other hand, the unit_tests folder will test the individual
functions themselves, making sure that passing in specific sets of arguments will return the correct response and other
sets will break the function intentionally.

"""

import hashlib
import os
import re
import unittest

from inspect import stack, getframeinfo


class BaseTestCase(unittest.TestCase):
    def __init__(self, methodName):
        super(BaseTestCase, self).__init__(methodName)
        current_frame = stack()[1]
        file_of_current_frame = current_frame[0].f_globals.get('__file__', None)
        dir_path_to_current_frame = os.path.dirname(file_of_current_frame)
        name_of_last_folder = dir_path_to_current_frame.split("/")[-1]
        self.class_name = name_of_last_folder + "/" + self.__class__.__name__

    def get_line_number(self):
        current_frame = stack()[1][0]
        frameinfo = getframeinfo(current_frame)
        return frameinfo.lineno

    def assertIn(self, substring, string_to_check, msg=None):
        self.failIf(substring not in string_to_check, msg=msg)

    def assertNotIn(self, substring, string_to_check, msg=None):
        self.failIf(substring in string_to_check, msg=msg)

    def get_unique_short_string(self, super_long_string):
        m = hashlib.md5()
        m.update(self.strip_whitespace(super_long_string))
        return repr(m.digest())

    def strip_whitespace(self, string):
        lines = string.split("\n")
        to_return = ""
        for line in lines:
            if isinstance(line, str):
                line = re.sub("[\t\r\n]+", "", line)  # Remove tabs and new-lines
                line = re.sub("[ ]{2,}", " ", line)  # Remove multiple spaces and replace with single spaces
                if len(line) > 1:  # Only add lines that are more than just a \n character
                    to_return += line + "\n"
        return to_return
