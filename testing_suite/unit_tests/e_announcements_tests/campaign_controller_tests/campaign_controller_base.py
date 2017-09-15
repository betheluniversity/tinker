from testing_suite.unit_tests import UnitTestCase
from tinker.e_announcements import CampaignController


class CampaignControllerBaseTestCase(UnitTestCase):
    def __init__(self, methodName):
        super(CampaignControllerBaseTestCase, self).__init__(methodName)
        self.controller = CampaignController()