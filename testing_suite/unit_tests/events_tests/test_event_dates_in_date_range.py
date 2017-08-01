from datetime import datetime, timedelta

from events_controller_base import EventsControllerBaseTestCase


class EventDatesInDateRangeTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(EventDatesInDateRangeTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_event_dates_in_date_range(self):

        def datetime_to_timestamp(dt):
            return self.controller.date_str_to_timestamp(dt.strftime('%B %d %Y, %I:%M %p'))/1000

        start = datetime(2017, 8, 16)
        end = datetime(2017, 8, 20)
        # Case 1: Event entirely outside search range
        case_1 = [{
            'start': datetime_to_timestamp(datetime(2017, 8, 15)),
            'end': datetime_to_timestamp(datetime(2017, 8, 21))
        }]
        response = self.controller.event_dates_in_date_range(case_1, start, end)
        self.assertTrue(response)
        # Case 2: Event entirely inside search range
        case_2 = [{
            'start': datetime_to_timestamp(datetime(2017, 8, 17)),
            'end': datetime_to_timestamp(datetime(2017, 8, 19))
        }]
        response = self.controller.event_dates_in_date_range(case_2, start, end)
        self.assertTrue(response)
        # Case 3: Event starts before range start, ends inside range
        case_3 = [{
            'start': datetime_to_timestamp(datetime(2017, 8, 15)),
            'end': datetime_to_timestamp(datetime(2017, 8, 19))
        }]
        response = self.controller.event_dates_in_date_range(case_3, start, end)
        self.assertTrue(response)
        # Case 4: Event starts during range, ends after range end
        case_4 = [{
            'start': datetime_to_timestamp(datetime(2017, 8, 17)),
            'end': datetime_to_timestamp(datetime(2017, 8, 21))
        }]
        response = self.controller.event_dates_in_date_range(case_4, start, end)
        self.assertTrue(response)
        # Case 5: Event ends before range start (fail)
        case_5 = [{
            'start': datetime_to_timestamp(datetime(2017, 8, 13)),
            'end': datetime_to_timestamp(datetime(2017, 8, 15))
        }]
        response = self.controller.event_dates_in_date_range(case_5, start, end)
        self.assertFalse(response)
        # Case 6: Event starts after range end (fail)
        case_6 = [{
            'start': datetime_to_timestamp(datetime(2017, 8, 21)),
            'end': datetime_to_timestamp(datetime(2017, 8, 23))
        }]
        response = self.controller.event_dates_in_date_range(case_6, start, end)
        self.assertFalse(response)
