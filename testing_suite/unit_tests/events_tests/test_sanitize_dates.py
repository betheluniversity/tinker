from events_controller_base import EventsControllerBaseTestCase


class SanitizeDatesTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SanitizeDatesTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_sanitize_dates(self):
        test_dates_list = [
            {
                'all_day': '::CONTENT-XML-CHECKBOX::No',
            },
            {
                'all_day': '::CONTENT-XML-CHECKBOX::',
            },
            {
                'outside_of_minnesota': '::CONTENT-XML-CHECKBOX::No'
            },
            {
                'outside_of_minnesota': '::CONTENT-XML-CHECKBOX::'
            }
        ]
        response = self.controller.sanitize_dates(test_dates_list)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), len(test_dates_list))
        for item in response:
            self.assertTrue(isinstance(item, dict))
            self.assertNotEqual(len(item.keys()), 0)
            value = item[item.keys()[0]]  # Get the value stored at the only key in each dictionary
            self.assertTrue(value is None)
