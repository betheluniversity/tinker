from unit_tests import BaseTestCase


class DeleteConfirmTestCase(BaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(DeleteConfirmTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = self.generate_url("delete_confirm")

    #######################
    ### Testing methods ###
    #######################

    def test_delete_confirm(self):
        expected_response = b'Your faculty bio has been deleted. It will be removed from your'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
