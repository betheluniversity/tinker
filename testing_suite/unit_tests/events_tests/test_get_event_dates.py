from events_controller_base import EventsControllerBaseTestCase


class GetEventDatesTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetEventDatesTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_event_dates(self):
        test_form = {
            'num_dates': 1,
            'start1': u'August 3rd 2017, 12:00 am',
            'end1': u'August 5th 2017, 12:00 am'
        }
        response = self.controller.get_event_dates(test_form)
        self.assertTrue(isinstance(response, tuple))
        self.assertTrue(isinstance(response[0], list))
        self.assertEqual(len(response[0]), 1)
        self.assertTrue(isinstance(response[0][0], dict))
        expected_keys = ['end_date', 'outside_of_minnesota', 'time_zone', 'all_day', 'no_end_date', 'start_date']
        for key in response[0][0].keys():
            self.assertTrue(key in expected_keys)
        self.assertTrue(isinstance(response[1], int))
        self.assertEqual(response[1], 1)
