from testing_suite.unit_tests import UnitTestCase
from tinker.e_announcements import EAnnouncementsController


class EAnnouncementsControllerBaseTestCase(UnitTestCase):
    def __init__(self, methodName):
        super(EAnnouncementsControllerBaseTestCase, self).__init__(methodName)
        self.controller = EAnnouncementsController()
