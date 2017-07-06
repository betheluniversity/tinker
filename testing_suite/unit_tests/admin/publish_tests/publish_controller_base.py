import unittest
from tinker.admin.publish import PublishManagerController


class PublishControllerBaseTestCase(unittest.TestCase):
    def __init__(self, methodName):
        super(PublishControllerBaseTestCase, self).__init__(methodName)
        self.controller = PublishManagerController()

    def setUp(self):
        pass

    def assertIn(self, substring, string_to_check, msg=None):
        self.failIf(substring not in string_to_check, msg=msg)

    def assertNotIn(self, substring, string_to_check, msg=None):
        self.failIf(substring in string_to_check, msg=msg)

    def tearDown(self):
        pass