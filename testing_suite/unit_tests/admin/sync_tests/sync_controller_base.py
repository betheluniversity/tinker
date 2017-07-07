from testing_suite.unit_tests import BaseUnitTestCase
from tinker.admin.sync import SyncController


class SyncControllerBaseTestCase(BaseUnitTestCase):
    def __init__(self, methodName):
        super(SyncControllerBaseTestCase, self).__init__(methodName)
        self.controller = SyncController()
