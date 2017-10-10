from testing_suite.unit_tests import UnitTestCase
from tinker.events import EventsController


class EventsControllerBaseTestCase(UnitTestCase):
    def __init__(self, methodName):
        super(EventsControllerBaseTestCase, self).__init__(methodName)
        self.controller = EventsController()
