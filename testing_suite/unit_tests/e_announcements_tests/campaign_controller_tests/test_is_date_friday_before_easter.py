from datetime import datetime

from campaign_controller_base import CampaignControllerBaseTestCase


class IsDateFridayBeforeEasterTestCase(CampaignControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IsDateFridayBeforeEasterTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_is_date_friday_before_easter(self):
        friday_before_easter = datetime(2017, 4, 14)
        response = self.controller.is_date_friday_before_easter(friday_before_easter)
        self.assertTrue(response)

        friday_after_easter = datetime(2017, 4, 21)
        response = self.controller.is_date_friday_before_easter(friday_after_easter)
        self.assertFalse(response)
