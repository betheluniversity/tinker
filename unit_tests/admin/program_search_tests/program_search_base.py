import os
import shutil
import tempfile
import tinker
from unit_tests import BaseTestCase


class ProgramSearchBaseTestCase(BaseTestCase):

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        os.environ['unit_testing'] = "True"
        self.temp_dir = tempfile.gettempdir()
        self.temp_path = os.path.join(self.temp_dir, 'tempCSV.csv')
        self.permanent_path = tinker.app.config['PROGRAM_SEARCH_CSV']
        shutil.copy2(tinker.app.config['PROGRAM_SEARCH_CSV'], self.temp_path)
        tinker.app.config['PROGRAM_SEARCH_CSV'] = self.temp_path
        tinker.app.testing = True
        tinker.app.config['ENVIRON'] = "test"
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        tinker.app.config['WTF_CSRF_METHODS'] = []
        self.app = tinker.app.test_client()

    # Corresponding to the setUp method, this method deletes the temporary database
    def tearDown(self):
        tinker.app.config['PROGRAM_SEARCH_CSV'] = self.permanent_path
        os.remove(self.temp_path)
