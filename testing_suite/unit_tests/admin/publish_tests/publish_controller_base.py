from testing_suite.unit_tests import UnitTestCase
from tinker.admin.publish import PublishManagerController


class PublishControllerBaseTestCase(UnitTestCase):
    def __init__(self, methodName):
        super(PublishControllerBaseTestCase, self).__init__(methodName)
        self.controller = PublishManagerController()
