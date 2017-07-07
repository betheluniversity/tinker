from testing_suite.unit_tests import BaseUnitTestCase
from tinker import app
from tinker.admin.program_search import ProgramSearchController


class ProgramSearchControllerBaseTestCase(BaseUnitTestCase):
    def __init__(self, methodName):
        super(ProgramSearchControllerBaseTestCase, self).__init__(methodName)
        self.controller = ProgramSearchController()

    def setUp(self):
        app.config['UNIT_TESTING'] = True
        self.old_csv_path = app.config['PROGRAM_SEARCH_CSV']
        app.config['PROGRAM_SEARCH_CSV'] = './programs.csv'

    def tearDown(self):
        app.config['UNIT_TESTING'] = False
        app.config['PROGRAM_SEARCH_CSV'] = self.old_csv_path
