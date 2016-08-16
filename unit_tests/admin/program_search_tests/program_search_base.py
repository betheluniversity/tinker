import os
import shutil
import tempfile
import tinker
import unittest


class ProgramSearchBaseTestCase(unittest.TestCase):

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        self.temp_dir = tempfile.gettempdir()
        self.temp_path = os.path.join(self.temp_dir, 'tempCSV.csv')
        self.permanent_path = tinker.app.config['PROGRAM_SEARCH_CSV']
        shutil.copy2(tinker.app.config['PROGRAM_SEARCH_CSV'], self.temp_path)
        tinker.app.config['PROGRAM_SEARCH_CSV'] = self.temp_path
        tinker.app.testing = True
        # Sadly, need to disable CSRF for these tests. :(
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        self.app = tinker.app.test_client()

    def send_post(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True)

    def send_get(self, url):
        return self.app.get(url, follow_redirects=True)

    def send_data(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True, content_type="application/json;charset=UTF-8")

    def get_csrf_token(self, url):
        import re
        response = self.send_get(url)
        # Returns 3rd parentheses group
        csrf_token = re.search('<input(.*)id="csrf_token"(.*)value="(.+)"(/?)>', response.data).group(3)
        return csrf_token

    # Corresponding to the setUp method, this method deletes the temporary database
    def tearDown(self):
        tinker.app.config['PROGRAM_SEARCH_CSV'] = self.permanent_path
        os.remove(self.temp_path)
        # pass

if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
