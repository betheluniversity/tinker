from testing_suite.unit_tests import UnitTestCase
from tinker.faculty_bios import FacultyBioController


class FacultyBiosControllerBaseTestCase(UnitTestCase):
    def __init__(self, methodName):
        super(FacultyBiosControllerBaseTestCase, self).__init__(methodName)
        self.controller = FacultyBioController()
