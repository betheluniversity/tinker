from redirects_base import RedirectsBaseTestCase


class NewRedirectSubmitTestCase(RedirectsBaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(NewRedirectSubmitTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("new_redirect_submit")

    def create_form(self, from_path="/from?", to_url="to!"):
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
        form = self.create_form()
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)
        # Add an assertion that it got added to the database
        # Delete the row that was just added
        self.send_post(self.generate_url("delete_redirect"), {'from_path': "/from?"})

    def test_new_redirect_submit_invalid(self):
        expected_response = self.ERROR_400
        arg_names = ['from_path', 'to_url']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: None}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/submit_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertIn(expected_response, response.data, msg=failure_message)
