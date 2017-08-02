from testing_suite.integration_tests import IntegrationTestCase


class ConfirmTestCase(IntegrationTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ConfirmTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = self.generate_url("confirm")

    #######################
    ### Testing methods ###
    #######################

    def test_confirm(self):
        expected_response = repr('\x10\x90x\x02\x07\xcf\xd3\xc7\xe0\xda\xea8\x13\xb3\x0c\x11')
        # b'You\'ll receive an email when your event has been approved by Conference and Event Services. Once your'
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)
