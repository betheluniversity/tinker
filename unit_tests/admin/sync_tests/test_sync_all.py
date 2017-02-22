from unit_tests import BaseTestCase


class AllTestCase(BaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(AllTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("all")

    #######################
    ### Testing methods ###
    #######################

    def test_all_valid(self):
        expected_response = b'<h3>Successfully Synced'
        response = self.send_post(self.request, {})
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)