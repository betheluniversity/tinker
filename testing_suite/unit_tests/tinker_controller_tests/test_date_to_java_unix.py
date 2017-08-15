from tinker_controller_base import TinkerControllerBaseTestCase


class DateToJavaUnixTestCase(TinkerControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(DateToJavaUnixTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_date_to_java_unix(self):
        test_date = 'August 18 2017, 3:42 pm'
        response = self.controller.date_to_java_unix(test_date)
        self.assertTrue(isinstance(response, int))
        self.assertTrue(response > 1500000000000)
