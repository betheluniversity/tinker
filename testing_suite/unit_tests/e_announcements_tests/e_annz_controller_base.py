from testing_suite.unit_tests import BaseUnitTestCase
from tinker.e_announcements import EAnnouncementsController


class EAnnouncementsControllerBaseTestCase(BaseUnitTestCase):
    def __init__(self, methodName):
        super(EAnnouncementsControllerBaseTestCase, self).__init__(methodName)
        self.controller = EAnnouncementsController()
