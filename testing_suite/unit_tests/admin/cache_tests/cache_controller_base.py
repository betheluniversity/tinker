from testing_suite.unit_tests import UnitTestCase
from tinker.admin.cache import CacheController


class CacheControllerBaseTestCase(UnitTestCase):
    def __init__(self, methodName):
        super(CacheControllerBaseTestCase, self).__init__(methodName)
        self.controller = CacheController()
