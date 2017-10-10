from tinker_controller_base import TinkerControllerBaseTestCase


class JavaUnixToDateTestCase(TinkerControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(JavaUnixToDateTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_java_unix_to_date(self):
        test_timestamp = 1503088920000
        response = self.controller.java_unix_to_date(test_timestamp)
        self.assertTrue(isinstance(response, str))
        self.assertTrue('August 18 2017' in response)
