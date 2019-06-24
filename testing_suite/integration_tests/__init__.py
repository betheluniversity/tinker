# Currently, the testing suite takes about 4 minutes to run.

import base64
import os
import re
import unittest
from inspect import stack

from selenium import webdriver

import tinker
from testing_suite import BaseTestCase
from testing_suite.utilities import get_tests_in_this_dir
from tinker import get_url_from_path


class IntegrationTestCase(BaseTestCase):
    def __init__(self, methodName):
        super(IntegrationTestCase, self).__init__(methodName)
        self.ERROR_400 = repr('\xad\xa0\xa0\xff;\x0e\x0bVx\xda\x99\x8c\xb8U\xc3\xb8')
        self.ERROR_500 = '<h1 class="oversized">Whoops! Tinker lost its connection.</h1>'

    def setUp(self):
        tinker.app.testing = True
        tinker.app.debug = False
        tinker.app.config['ENVIRON'] = "test"
        tinker.app.config['UNIT_TESTING'] = True
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        tinker.app.config['WTF_CSRF_METHODS'] = []
        self.app = tinker.app.test_client()

    # todo: this needs to be walked through and heavily commented, if we keep it.
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
        endpoint_path = flask_classy_name + ":" + method_name
        return get_url_from_path(endpoint_path, **kwargs)

    def send_get(self, url, basic_auth=False):
        if basic_auth:
            to_base64 = tinker.app.config['CASCADE_LOGIN']['username'] + ":" + tinker.app.config['CASCADE_LOGIN'][
                'password']
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

    # todo: if we change our comparisons, this will probably also need to be updated.
    def generate_failure_message(self, type, request, response_data, expected_response, class_name, line_number):
        return '"%(0)s %(1)s" received "%(2)s" when it was expecting "%(3)s" in %(4)s on line %(5)s.' % \
               {'0': type, '1': request, '2': self.get_useful_string(response_data), '3': expected_response,
                '4': class_name, '5': line_number}

    # todo: rename
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
