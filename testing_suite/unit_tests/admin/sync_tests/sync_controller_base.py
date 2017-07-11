from testing_suite.unit_tests import UnitTestCase
from tinker.admin.sync import SyncController


class SyncControllerBaseTestCase(UnitTestCase):
    def __init__(self, methodName):
        super(SyncControllerBaseTestCase, self).__init__(methodName)
        self.controller = SyncController()
