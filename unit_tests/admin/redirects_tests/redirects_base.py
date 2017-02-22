from flask_fixtures import FixturesMixin
from flask_sqlalchemy import SQLAlchemy

import tinker
from unit_tests import BaseTestCase


class RedirectsBaseTestCase(BaseTestCase, FixturesMixin):

    # fixtures = ['test_database.json']
    tinker_app = tinker.app
    tinker_app.testing = True
    tinker_app.debug = False
    tinker_app.config['ENVIRON'] = "test"
    base_uri = tinker_app.config['SQLALCHEMY_DATABASE_URI'].split("app.db")[0]
    tinker_app.config['SQLALCHEMY_DATABASE_URI'] = base_uri + "testing_db.db"
    tinker_app.config['WTF_CSRF_ENABLED'] = False
    tinker_app.config['WTF_CSRF_METHODS'] = []
    db = SQLAlchemy(tinker_app)

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        self.app = self.tinker_app.test_client()
