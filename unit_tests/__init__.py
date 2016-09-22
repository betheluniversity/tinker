# In an ideal world, here are some features that I would like to implement to unit testing:
# 1. Make the unit tests much more robust; instead of just testing endpoints of a module, it can also check that each
#       respective DB or Cascade object gets updated appropriately so that there's no possibility of silent failures
# 2. Find some way to pass test object ids back and forth between unit tests so that the test_sequentially files can be
#       split into individual, granular unit tests.
#
# Currently, the unit testing suite takes about 3 minutes to run.

import os
os.environ['unit_testing'] = "True"
import re
import tinker
import unittest
from inspect import stack
from tinker import get_url_from_path
from unit_test_utilities import get_tests_in_this_dir


class BaseTestCase(unittest.TestCase):

    def __init__(self, methodName):
        super(BaseTestCase, self).__init__(methodName)
        self.ERROR_400 = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        self.ERROR_404 = b'<h1 class="oversized"> It\'s probably not a problem, probably.</h1>'
        self.ERROR_500 = b'fixing the loose wire right now. Check back soon!</h5>'
        current_frame = stack()[1]
        file_of_current_frame = current_frame[0].f_globals.get('__file__', None)
        dir_path_to_current_frame = os.path.dirname(file_of_current_frame)
        name_of_last_folder = dir_path_to_current_frame.split("/")[-1]
        self.class_name = name_of_last_folder + "/" + self.__class__.__name__

    def setUp(self):
        tinker.app.testing = True
        tinker.app.config['ENVIRON'] = "test"
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        tinker.app.config['WTF_CSRF_METHODS'] = []
        self.app = tinker.app.test_client()

    def generate_url(self, method_name, **kwargs):
        current_frame = stack()[1]
        file_of_current_frame = current_frame[0].f_globals.get('__file__', None)
        dir_path_to_current_frame = os.path.dirname(file_of_current_frame)
        name_of_last_folder = dir_path_to_current_frame.split("/")[-1]
        local_folder_name = name_of_last_folder.split("_tests")[0]
        flask_classy_name = ""
        words_in_folder_name = local_folder_name.split("_")
        for word in words_in_folder_name:
            flask_classy_name += word.capitalize()
        flask_classy_name += "View"
        endpoint_path = local_folder_name + "." + flask_classy_name + ":" + method_name
        return get_url_from_path(endpoint_path, **kwargs)

    def send_get(self, url):
        return self.app.get(url, follow_redirects=True)

    def send_post(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True)

    def generate_failure_message(self, type, request, response_data, expected_response, class_name):
        return '"%(0)s %(1)s" received "%(2)s" when it was expecting "%(3)s" in %(4)s.' % \
               {'0': type, '1': request, '2': self.get_useful_string(response_data), '3': expected_response,
                '4': class_name}

    def assertIn(self, substring, string_to_check, msg=None):
        self.failIf(substring not in string_to_check, msg=msg)

    def assertNotIn(self, substring, string_to_check, msg=None):
        self.failIf(substring in string_to_check, msg=msg)

    def strip_whitespace(self, string):
        lines = string.split("\n")
        to_return = ""
        for line in lines:
            if isinstance(line, str):
                line = re.sub("[\t\r\n]+", "", line)  # Remove tabs and new-lines
                line = re.sub("[ ]{2,}", " ", line)  # Remove multiple spaces and replace with single spaces
                if len(line) > 1:
                    to_return += line + "\n"
        return to_return

    def get_useful_string(self, string_of_html):
        if "</nav>" in string_of_html and "<footer class=\"footer\">" in string_of_html:
            pattern = re.compile(r'</nav>(.+)<footer class="footer">', re.DOTALL)
            to_return = re.search(pattern, string_of_html).group(1)
        elif "<body>" in string_of_html and "</body>" in string_of_html:
            pattern = re.compile(r'<body>(.+)</body>', re.DOTALL)
            to_return = re.search(pattern, string_of_html).group(1)
        else:
            to_return = string_of_html
        return self.strip_whitespace(to_return)

    def tearDown(self):
        pass


if __name__ == "__main__":
    testsuite = get_tests_in_this_dir(".")
    unittest.TextTestRunner(verbosity=1).run(testsuite)


# Missing unit test files:
# admin/redirects/new_api_submit
# admin/redirects/new_api_submit_asset_expiration
# admin/redirects/new_internal_redirect_submit
