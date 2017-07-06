import unittest
from tinker import app
from tinker.admin.program_search import ProgramSearchController


class ProgramSearchControllerBaseTestCase(unittest.TestCase):
    def __init__(self, methodName):
        super(ProgramSearchControllerBaseTestCase, self).__init__(methodName)
        self.controller = ProgramSearchController()

    def setUp(self):
        self.old_csv_path = app.config['PROGRAM_SEARCH_CSV']
        app.config['PROGRAM_SEARCH_CSV'] = './programs.csv'

    def assertIn(self, substring, string_to_check, msg=None):
        self.failIf(substring not in string_to_check, msg=msg)

    def assertNotIn(self, substring, string_to_check, msg=None):
        self.failIf(substring in string_to_check, msg=msg)

    def tearDown(self):
        app.config['PROGRAM_SEARCH_CSV'] = self.old_csv_path
