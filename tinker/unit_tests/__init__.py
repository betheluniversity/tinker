# In an ideal world, here are some features that I would like to implement to unit testing:
# 1. Integrate the unit tests into the Travis checker plugin for github, so that all changes will automatically get
#       tested by the unit tests
# 2. Make the unit tests much more robust; instead of just testing endpoints of a module, it can also check that each
#       respective DB or Cascade object gets updated appropriately so that there's no possibility of silent failures
# 3. Find some way to pass test object ids back and forth between unit tests so that the test_sequentially files can be
#       split into individual, granular unit tests.
# 4. Write a unit test factory class that can auto-generate unit test files given a set of parameters about the endpoint
#       it's going to be testing.
#
# Currently, the unit testing suite takes about 2 minutes to run.

import sys
import tinker
import unittest


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        tinker.app.testing = True
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        tinker.app.config['WTF_CSRF_METHODS'] = []
        self.app = tinker.app.test_client()

    def send_get(self, url):
        return self.app.get(url, follow_redirects=True)

    def send_post(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True)

    def generate_failure_message(self, request, response_data, expected_response, class_name):
        return '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
               {'0': request, '1': response_data, '2': expected_response, '3': class_name}

    def tearDown(self):
        pass


if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover('.')
    runner = unittest.TextTestRunner(verbosity=1).run(testsuite)
    sys.exit(len(runner.failures))


# Missing unit test files:
# admin/redirects/new_api_submit
# admin/redirects/new_api_submit_asset_expiration
# admin/redirects/new_internal_redirect_submit
# e_announcements/edit_all
# events/confirm
# events/edit_all
# events/reset_tinker_edits
# faculty_bio/confirm
# faculty_bio/delete_confirm
# faculty_bio/activate
# faculty_bio/edit_all
# office_hours/rotate_hours
