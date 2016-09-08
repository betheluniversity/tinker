import os
import platform
import shutil
import tempfile
import unittest

import tinker
from unit_tests import BaseTestCase


# @unittest.skipIf("testing" in platform.node(), "Travis CI can't do Redirects unit tests right now, so hopefully this "
#                                                "should skip them all")
class RedirectsBaseTestCase(BaseTestCase):

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        self.temp_dir = tempfile.gettempdir()
        self.temp_path = os.path.join(self.temp_dir, 'tempDB.db')
        self.permanent_path = tinker.app.config['SQLALCHEMY_DATABASE_URI']
        shutil.copy2(tinker.app.config['SQLALCHEMY_DATABASE_URI'].split('sqlite://')[1], self.temp_path)
        tinker.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.temp_path
        tinker.app.testing = True
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        tinker.app.config['WTF_CSRF_METHODS'] = []
        self.app = tinker.app.test_client()

    # Corresponding to the setUp method, this method deletes the temporary database
    def tearDown(self):
        tinker.app.config['SQLALCHEMY_DATABASE_URI'] = self.permanent_path
        os.remove(self.temp_path)