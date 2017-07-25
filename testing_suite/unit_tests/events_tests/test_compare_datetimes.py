from datetime import timedelta
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

    def test_compare_time_deltas(self):
        # A second longer than 24 hours
        a = timedelta(days=1, seconds=1)
        # A second shorter than 24 hours
        b = timedelta(hours=23, minutes=59, seconds=59)
        self.assertTrue(self.controller.compare_datetimes(a, b) == 1)
        self.assertTrue(self.controller.compare_datetimes(b, a) == -1)
        b = timedelta(days=1, seconds=1)
        self.assertTrue(self.controller.compare_datetimes(a, b) == 0)
        self.assertTrue(self.controller.compare_datetimes(b, a) == 0)


