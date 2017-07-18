from datetime import datetime
from campaign_controller_base import CampaignControllerBaseTestCase


class IsBethelHolidayTestCase(CampaignControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IsBethelHolidayTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_is_bethel_holiday(self):
        # Assert new years is a holiday
        test_date = datetime(2017, 1, 1)
        response = self.controller.is_bethel_holiday(test_date)
        self.assertTrue(response)

        # Assert new years' observed
        test_date = datetime(2017, 1, 2)
        response = self.controller.is_bethel_holiday(test_date)
        self.assertTrue(response)

        # Assert MLK Day
        test_date = datetime(2017, 1, 16)
        response = self.controller.is_bethel_holiday(test_date)
        self.assertTrue(response)

        # Assert Memorial Day
        test_date = datetime(2017, 5, 29)
        response = self.controller.is_bethel_holiday(test_date)
        self.assertTrue(response)

        # Assert July 4th
        test_date = datetime(2017, 7, 4)
        response = self.controller.is_bethel_holiday(test_date)
        self.assertTrue(response)

        # Assert Labor Day
        test_date = datetime(2017, 9, 4)
        response = self.controller.is_bethel_holiday(test_date)
        self.assertTrue(response)

        # Assert black Friday
        test_date = datetime(2017, 11, 24)
        response = self.controller.is_bethel_holiday(test_date)
        self.assertTrue(response)

        # Assert Christmas eve observed
        test_date = datetime(2016, 12, 23)
        response = self.controller.is_bethel_holiday(test_date)
        self.assertTrue(response)

        # Assert any given day in 12/24 - 12/31
        for date in [datetime(2017, 12, number) for number in range(24, 32)]:
            response = self.controller.is_bethel_holiday(date)
            self.assertTrue(response)

        # Assert not any other day
        test_date = datetime(2016, 12, 21)
        response = self.controller.is_bethel_holiday(test_date)
        self.assertFalse(response)
