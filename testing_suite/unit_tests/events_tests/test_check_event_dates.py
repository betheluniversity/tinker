from events_controller_base import EventsControllerBaseTestCase


class CheckEventDatesTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CheckEventDatesTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_check_event_dates_valid(self):
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
        response = self.controller.check_event_dates(test_event_dates)
        self.assertTrue(isinstance(response, tuple))
        self.assertEqual(len(response), 2)
        self.assertTrue(isinstance(response[0], str))
        expected_response = '[{"end_date": "August 5th 2017, 12:00 am", "outside_of_minnesota": "", "all_day": "", ' \
                            '"time_zone": "", "no_end_date": "", "start_date": "August 3rd 2017, 12:00 am"}]'
        self.assertEqual(response[0], expected_response)
        self.assertTrue(isinstance(response[1], bool))
        self.assertTrue(response[1])

    def test_check_event_dates_invalid(self):
        test_event_dates = [
            {
                'start_date': u'August 3rd 2017, 12:00 am',
                'end_date': u'August 1st 2017, 12:00 am',
                'outside_of_minnesota': '',
                'time_zone': u'',
                'all_day': '',
                'no_end_date': '',
            }
        ]
        response = self.controller.check_event_dates(test_event_dates)
        self.assertTrue(isinstance(response, tuple))
        self.assertEqual(len(response), 2)
        self.assertTrue(isinstance(response[1], bool))
