import sqlite3
import tinker
from StringIO import StringIO
from unit_tests import BaseTestCase


class RedirectsBaseTestCase(BaseTestCase):

    def create_temp_db(self):
        # Read database to tempfile
        app = tinker.app
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].split('sqlite:///')[1].split('app.db')[0] + "testing_db.db"
        # print db_path
        con = sqlite3.connect(db_path)
        tempfile = StringIO()
        for line in con.iterdump():
            tempfile.write('%s\n' % line)
        con.close()
        tempfile.seek(0)

        # Create a database in memory and import from tempfile
        app.sqlite = sqlite3.connect(":memory:")
        app.sqlite.cursor().executescript(tempfile.read())
        app.sqlite.commit()
        app.sqlite.row_factory = sqlite3.Row
        return app.sqlite

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        self.permanent_db_reference = tinker.db
        tinker.db = self.create_temp_db()
        tinker.app.testing = True
        tinker.app.config['ENVIRON'] = "test"
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        tinker.app.config['WTF_CSRF_METHODS'] = []
        self.app = tinker.app.test_client()

    # Corresponding to the setUp method, this method deletes the temporary database
    def tearDown(self):
        tinker.db = self.permanent_db_reference
