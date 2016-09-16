from redirects_base import RedirectsBaseTestCase


class DeleteTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(DeleteTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = self.generate_url("delete_redirect")

    def create_form(self, from_path):
        return {
            'from_path': from_path
        }

    #######################
    ### Testing methods ###
    #######################

    def test_delete_valid(self):
        expected_response = b'delete'
        form_contents = self.create_form("/development")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_delete_invalid_path(self):
        expected_response = b'fail'
        form_contents = self.create_form("/from?")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)