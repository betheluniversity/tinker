from redirects_base import RedirectsBaseTestCase


class NewApiSubmitTestCase(RedirectsBaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(NewApiSubmitTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("new_api_submit")

    def create_new_form_submission(self, from_path, to_url):
        return {
            'body': "redirect: %s %s" % (from_path, to_url)
        }

    #######################
    ### Testing methods ###
    #######################

    def test_new_api_submit_valid(self):
        expected_response = b'<Redirect /from? to to!>'
        form_contents = self.create_new_form_submission("/from?", "to!")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)
        # Add an assertion that it got added to the database
        # Delete the row that was just added
        self.send_post(self.generate_url("delete_redirect"), {'from_path': "/from?"})
