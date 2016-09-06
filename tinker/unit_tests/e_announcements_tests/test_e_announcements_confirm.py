from tinker.unit_tests import BaseTestCase


class ConfirmTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ConfirmTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /e-announcement/confirm"

    #######################
    ### Testing methods ###
    #######################

    def test_confirm(self):
        expected_response = b"You've successfully created your E-Announcement. Once your E-Announcement has been approved,"
        response = self.send_get("/e-announcement/confirm")
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
