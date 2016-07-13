import os
import shutil
import tempfile
import tinker
import unittest


class EAnnouncementsBaseTestCase(unittest.TestCase):

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        self.temp_dir = tempfile.gettempdir()
        self.temp_path = os.path.join(self.temp_dir, 'tempDB.db')
        self.permanent_path = tinker.app.config['SQLALCHEMY_DATABASE_URI']
        shutil.copy2(tinker.app.config['SQLALCHEMY_DATABASE_URI'].split('sqlite://')[1], self.temp_path)
        tinker.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.temp_path
        self.app = tinker.app.test_client()

    def send_post(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True)

    def send_get(self, url):
        return self.app.get(url, follow_redirects=True)

    # Corresponding to the setUp method, this method deletes the temporary database
    def tearDown(self):
        tinker.app.config['SQLALCHEMY_DATABASE_URI'] = self.permanent_path
        os.remove(self.temp_path)

if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
