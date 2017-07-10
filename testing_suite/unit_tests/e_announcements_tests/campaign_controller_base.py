from testing_suite.unit_tests import BaseUnitTestCase
from tinker.e_announcements import CampaignController


class CampaignControllerBaseTestCase(BaseUnitTestCase):
    def __init__(self, methodName):
        super(CampaignControllerBaseTestCase, self).__init__(methodName)
        self.controller = CampaignController()