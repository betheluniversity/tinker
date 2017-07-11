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
        expected_response = repr('\xb7\xda\xa0)l\xa8\x9c\xd2\xf1\x12\x11\xc7\xabG\x93\x97')
        # b'You\'ll receive an email when your event has been approved by Conference and Event Services. Once your'
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)
