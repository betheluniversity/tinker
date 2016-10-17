from unit_tests import BaseTestCase


class EditAllTestCase(BaseTestCase):

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
        expected_response = b'success'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)