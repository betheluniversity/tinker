from datetime import datetime

from events_controller_base import EventsControllerBaseTestCase


class CompareDateTimesTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CompareDateTimesTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_compare_time_datetimes(self):
        # Christmas
        a = datetime(2017, 12, 25)
        # Eve
        b = datetime(2017, 12, 24)
        self.assertEqual(self.controller.compare_datetimes(a, b), 1)
        self.assertEqual(self.controller.compare_datetimes(b, a), -1)
        b = datetime(2017, 12, 25)
        self.assertEqual(self.controller.compare_datetimes(a, b), 0)
        self.assertEqual(self.controller.compare_datetimes(b, a), 0)


