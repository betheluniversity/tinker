import unittest
from tinker.admin.cache import CacheController


class CacheControllerBaseTestCase(unittest.TestCase):
    def __init__(self, methodName):
        super(CacheControllerBaseTestCase, self).__init__(methodName)
        self.controller = CacheController()

    def setUp(self):
        pass

    def tearDown(self):
        pass