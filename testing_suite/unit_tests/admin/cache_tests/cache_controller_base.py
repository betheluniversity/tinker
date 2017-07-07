from testing_suite.unit_tests import BaseUnitTestCase
from tinker.admin.cache import CacheController


class CacheControllerBaseTestCase(BaseUnitTestCase):
    def __init__(self, methodName):
        super(CacheControllerBaseTestCase, self).__init__(methodName)
        self.controller = CacheController()
