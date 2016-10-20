from redirects_base import RedirectsBaseTestCase


class NewRedirectSubmitTestCase(RedirectsBaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(NewRedirectSubmitTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("new_redirect_submit")

    def create_new_form_submission(self, from_path, to_url):
        return {
            'new-redirect-from': from_path,
            'new-redirect-to': to_url,
            'short-url': "on",
            'expiration-date': "Fri Jul 01 2016"
        }

    #######################
    ### Testing methods ###
    #######################

    def test_new_redirect_submit_valid(self):
        expected_response = b'<Redirect /from? to to!>'
        form_contents = self.create_new_form_submission("from?", "to!")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
        # Add an assertion that it got added to the database
        # Delete the row that was just added
        self.send_post(self.generate_url("delete_redirect"), {'from_path': "from?"})

    def test_new_redirect_submit_invalid_from(self):
        expected_response = self.ERROR_400
        form_contents = self.create_new_form_submission(None, "to!")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_new_redirect_submit_invalid_to(self):
        expected_response = self.ERROR_400
        form_contents = self.create_new_form_submission("from?", None)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)