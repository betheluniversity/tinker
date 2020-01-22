from testing_suite.unit_tests import UnitTestCase
from tinker.e_announcements import CampaignController
from tinker.e_announcements.e_announcements_controller import EAnnouncementsController


class CampaignControllerBaseTestCase(UnitTestCase):
    def __init__(self, methodName):
        super(CampaignControllerBaseTestCase, self).__init__(methodName)
        self.controller = CampaignController()
        self.base = EAnnouncementsController()