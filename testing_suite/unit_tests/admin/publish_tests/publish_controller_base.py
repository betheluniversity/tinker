from testing_suite.unit_tests import BaseUnitTestCase
from tinker.admin.publish import PublishManagerController


class PublishControllerBaseTestCase(BaseUnitTestCase):
    def __init__(self, methodName):
        super(PublishControllerBaseTestCase, self).__init__(methodName)
        self.controller = PublishManagerController()
