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
        expected_response = repr("'I\xf6\xa7*\x1c\x96\xc0\xbc\xf7\xba,\x92\\B\x8a")
        # b'Your faculty bio has been deleted. It will be removed from your'
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)
