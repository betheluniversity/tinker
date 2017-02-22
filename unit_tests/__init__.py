# Currently, the unit testing suite takes about 4 minutes to run.

import base64
import os
import re
import unittest
from inspect import stack, getframeinfo

import tinker
from tinker import get_url_from_path
from unit_test_utilities import get_tests_in_this_dir


class BaseTestCase(unittest.TestCase):

    def __init__(self, methodName):
        # from tinker.admin.redirects.models import BethelRedirect
        # print len(BethelRedirect.query.all())
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
        tinker.app.debug = False
        # tinker.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        tinker.app.config['ENVIRON'] = "test"
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        tinker.app.config['WTF_CSRF_METHODS'] = []
        self.app = tinker.app.test_client()

    def generate_url(self, method_name, **kwargs):
        current_frame = stack()[1][0]
        file_of_current_frame = current_frame.f_globals.get('__file__', None)
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

    def send_get(self, url, basic_auth=False):
        if basic_auth:
            to_base64 = tinker.app.config['CASCADE_LOGIN']['username'] + ":" + tinker.app.config['CASCADE_LOGIN']['password']
            auth_string = "Basic " + base64.b64encode(to_base64)
            return self.app.get(url, follow_redirects=True, headers={"Authorization": auth_string})
        else:
            return self.app.get(url, follow_redirects=True)

    def send_post(self, url, form_contents, basic_auth=False):
        if basic_auth:
            to_base64 = tinker.app.config['CASCADE_LOGIN']['username'] + ":" + tinker.app.config['CASCADE_LOGIN'][
                'password']
            auth_string = "Basic " + base64.b64encode(to_base64)
            return self.app.post(url, data=form_contents, follow_redirects=True, headers={"Authorization": auth_string})
        else:
            return self.app.post(url, data=form_contents, follow_redirects=True)

    def generate_failure_message(self, type, request, response_data, expected_response, class_name, line_number):
        return '"%(0)s %(1)s" received "%(2)s" when it was expecting "%(3)s" in %(4)s on line %(5)s.' % \
               {'0': type, '1': request, '2': self.get_useful_string(response_data), '3': expected_response,
                '4': class_name, '5': line_number}

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
                if len(line) > 1:  # Only add lines that are more than just a \n character
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

    def get_line_number(self):
        current_frame = stack()[1][0]
        frameinfo = getframeinfo(current_frame)
        return frameinfo.lineno

    def tearDown(self):
        pass


if __name__ == "__main__":
    testsuite = get_tests_in_this_dir(".")
    unittest.TextTestRunner(verbosity=1).run(testsuite)
