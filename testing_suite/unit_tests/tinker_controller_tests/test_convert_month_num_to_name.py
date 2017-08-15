from tinker_controller_base import TinkerControllerBaseTestCase


class ConvertMonthNumberToNameTestCase(TinkerControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ConvertMonthNumberToNameTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_convert_month_num_to_name(self):
        nums_to_dates = {
            '01': 'january',
            '02': 'february',
            '03': 'march',
            '04': 'april',
            '05': 'may',
            '06': 'june',
            '07': 'july',
            '08': 'august',
            '09': 'september',
            '10': 'october',
            '11': 'november',
            '12': 'december'

        }
        for number in nums_to_dates.keys():
            response = self.controller.convert_month_num_to_name(number)
            self.assertTrue(isinstance(response, str))
            self.assertEqual(response, nums_to_dates[number])
