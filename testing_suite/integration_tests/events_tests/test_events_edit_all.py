from testing_suite.integration_tests import IntegrationTestCase


class EditAllTestCase(IntegrationTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(EditAllTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = self.generate_url("edit_all")

    #######################
    ### Testing methods ###
    #######################

    def test_edit_all(self):
        expected_response = repr('\xaex\x05\x85\xf4\x9b\x94\xce\x14D\xeb}(\x90a#')  # b'success'
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)
