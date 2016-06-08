import os
import shutil
import tinker
import unittest
import tempfile


class RedirectsTestCase(unittest.TestCase):

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        self.temp_dir = tempfile.gettempdir()
        self.temp_path = os.path.join(self.temp_dir, 'tempDB.db')
        self.permanent_path = tinker.app.config['SQLALCHEMY_DATABASE_URI']
        shutil.copy2(tinker.app.config['SQLALCHEMY_DATABASE_URI'][9:], self.temp_path)
        tinker.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.temp_path
        tinker.app.config['DEBUG'] = True
        tinker.app.config['TESTING'] = True
        self.app = tinker.app.test_client()


    # All these middle methods are individual tests. unittest will automatically run all of these methods and tell you
    # which tests, if any, failed. If they all pass, then it says "OK"

    def test_new(self):
        form_contents = {'new-redirect-from': "from?",
                         'new-redirect-to': "to!",
                         'short-url': "on",
                         'expiration-date': "Fri Jul 01 2016"
                         }
        rv = self.app.post('/admin/redirect/new-submit', data=form_contents, follow_redirects=True)
        assert b'' in rv.data

    def test_search(self):
        form_contents = {'type': "from_path",
                         'search': "/"}
        rv = self.app.post('/admin/redirect/search', data=form_contents, follow_redirects=True)
        assert b'<span class="from_path">' in rv.data

    def test_delete(self):
        form_contents = {'from_path': "from?"}
        rv = self.app.post('/admin/redirect/delete', data=form_contents, follow_redirects=True)
        assert b'fail' in rv.data

    # Corresponding to the setUp method, this method unlinks the temporary database so that it can be released from RAM
    def tearDown(self):
        del tinker.app.config['DEBUG']
        del tinker.app.config['TESTING']
        tinker.app.config['SQLALCHEMY_DATABASE_URI'] = self.permanent_path
        os.remove(self.temp_path)

if __name__ == '__main__':
    unittest.main()
