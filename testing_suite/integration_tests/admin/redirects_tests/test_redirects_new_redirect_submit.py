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
        expected_response = repr('\x04\xaa\x91\x86j\x9ap=\xb1\x82\xdbB\x8f\x83\x8a\x06')
        # b'<Redirect /from? to to!>'
        form = self.create_form()
        response = self.send_post(self.request, form)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)
        # Add an assertion that it got added to the database
        # Delete the row that was just added
        self.send_post(self.generate_url("delete_redirect"), {'redirect_id': "16857"})

    def test_new_redirect_submit_invalid(self):
        expected_response = repr('\xd3/\xd0\x99\xb8\x9a\x9c\xa3l\x19\x06\xf1P\x9f9\xbd')
        arg_names = ['from_path', 'to_url']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: None}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            short_string = self.get_unique_short_string(response.data)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/submit_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertEqual(expected_response, short_string, msg=failure_message)
