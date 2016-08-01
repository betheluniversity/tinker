# import os
# import shutil
# import tempfile
import tinker
import unittest


class EAnnouncementsBaseTestCase(unittest.TestCase):

    def setUp(self):
        tinker.app.testing = True
        self.app = tinker.app.test_client()

    def send_post(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True)

    def send_get(self, url):
        return self.app.get(url, follow_redirects=True)

    def tearDown(self):
        pass

if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
