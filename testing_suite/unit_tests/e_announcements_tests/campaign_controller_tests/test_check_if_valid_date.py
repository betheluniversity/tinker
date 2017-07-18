from datetime import datetime
from campaign_controller_base import CampaignControllerBaseTestCase


class CheckIfValidDateTestCase(CampaignControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CheckIfValidDateTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_check_if_valid_date(self):
        # Friday, Dec 15th of this year should be the last valid day to run E-Announcements in 2017
        valid_date = datetime(2017, 12, 15)
        self.assertTrue(self.controller.check_if_valid_date(valid_date))

        # January 1st will hit the 'too early' check before it hits the 'holiday' check
        too_early_date = datetime(2017, 1, 1)
        self.assertFalse(self.controller.check_if_valid_date(too_early_date))

        # Check if it catches a Tuesday (should only allow M, W, F dates)
        tuesday_date = datetime(2017, 12, 26)
        self.assertFalse(self.controller.check_if_valid_date(tuesday_date))

        # This year's Christmas (Monday Dec 25th) should be invalid only because it's a holiday
        holiday_date = datetime(2017, 12, 25)
        self.assertFalse(self.controller.check_if_valid_date(holiday_date))
