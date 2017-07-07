import unittest

from flask_sqlalchemy import SQLAlchemy

from tinker import app, db
from tinker.admin.redirects import RedirectsController


class RedirectsControllerBaseTestCase(unittest.TestCase):
    def __init__(self, methodName):
        super(RedirectsControllerBaseTestCase, self).__init__(methodName)
        # base_uri = app.config['SQLALCHEMY_DATABASE_URI'].split("app.db")[0]
        # app.config['SQLALCHEMY_DATABASE_URI'] = base_uri + '/testing_db.db'
        # self.testing_db = SQLAlchemy(app)
        self.controller = RedirectsController(db)

    def setUp(self):
        self.old_redirects_path = app.config['REDIRECTS_FILE_PATH']
        app.config['REDIRECTS_FILE_PATH'] = './redirects.txt'

        # self.old_uri = app.config['SQLALCHEMY_DATABASE_URI']
        # base_uri = app.config['SQLALCHEMY_DATABASE_URI'].split("app.db")[0]
        # app.config['SQLALCHEMY_DATABASE_URI'] = base_uri + '/testing_db.db'

    def tearDown(self):
        app.config['REDIRECTS_FILE_PATH'] = self.old_redirects_path
        # app.config['SQLALCHEMY_DATABASE_URI'] = self.old_uri
