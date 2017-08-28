from testing_suite.unit_tests import UnitTestCase
from tinker import TinkerController


# For tinker_controller, I'm only writing tests for the methods that don't directly deal with Cascade and the methods
# that are clear input -> work -> output style. This excludes the vast majority of the methods, but I'm ok with that.
class TinkerControllerBaseTestCase(UnitTestCase):
    def __init__(self, methodName):
        super(TinkerControllerBaseTestCase, self).__init__(methodName)
        self.controller = TinkerController()
