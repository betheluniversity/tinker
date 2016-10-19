# import sqlite3
import tinker
# from StringIO import StringIO
from unit_tests import BaseTestCase


class RedirectsBaseTestCase(BaseTestCase):

    # fixtures = ['test_database.json']
    app = tinker.app
    db = tinker.db

    # def create_temp_db(self):
    #     # Read database to tempfile
    #     app = tinker.app
    #     db_path = app.config['SQLALCHEMY_DATABASE_URI'].split('sqlite:///')[1].split('app.db')[0] + "testing_db.db"
    #     con = sqlite3.connect(db_path)
    #     tempfile = StringIO()
    #     for line in con.iterdump():
    #         tempfile.write('%s\n' % line)
    #     con.close()
    #     tempfile.seek(0)
    #
    #     # Create a database in memory and import from tempfile
    #     mem_db = sqlite3.connect(":memory:")
    #     mem_db.cursor().executescript(tempfile.read())
    #     mem_db.commit()
    #     mem_db.row_factory = sqlite3.Row
    #     return mem_db

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        # self.permanent_db_reference = tinker.db
        # tinker.db = self.create_temp_db()
        tinker.app.testing = True
        # tinker.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        tinker.app.config['ENVIRON'] = "test"
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        tinker.app.config['WTF_CSRF_METHODS'] = []
        self.app = tinker.app.test_client()
        from tinker.admin.redirects.models import BethelRedirect
        print len(BethelRedirect.query.all())

    # Corresponding to the setUp method, this method deletes the temporary database
    def tearDown(self):
        # tinker.db = self.permanent_db_reference
        pass
