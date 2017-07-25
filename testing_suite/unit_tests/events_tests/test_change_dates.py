from events_controller_base import EventsControllerBaseTestCase


class ChangeDatesTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ChangeDatesTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_change_dates_valid(self):
        test_event_dates = [
            {
                'start_date': u'August 3rd 2017, 12:00 am',
                'end_date': u'August 5th 2017, 12:00 am',
                'outside_of_minnesota': '',
                'time_zone': u'',
                'all_day': '',
                'no_end_date': '',
            }
        ]
        response = self.controller.change_dates(test_event_dates)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(len(response) == len(test_event_dates))
        self.assertTrue(isinstance(response[0], dict))
        for expected_key in test_event_dates[0].keys():
            self.assertTrue(expected_key in response[0].keys())
        self.assertTrue(isinstance(response[0]['start_date'], int))
        self.assertTrue(isinstance(response[0]['end_date'], int))
        self.assertEqual(response[0]['all_day'], 'No')
        self.assertEqual(response[0]['outside_of_minnesota'], 'No')

    def test_change_dates_invalid(self):
        # This will fail because it's not in a list
        bad_event_dates = {
            'start_date': u'',
            'end_date': u'',
            'outside_of_minnesota': '',
            'time_zone': u'',
            'all_day': '',
            'no_end_date': '',
        }
        self.assertRaises(KeyError, self.controller.change_dates, bad_event_dates)
