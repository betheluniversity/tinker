from redirects_base import RedirectsBaseTestCase


class DeleteTestCase(RedirectsBaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(DeleteTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("delete_redirect")

    def create_form(self, redirect_id="16928"):
        return {
            'redirect_id': redirect_id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_delete_valid(self):
        # Create a row that can then be deleted immediately
        self.send_post(self.generate_url("new_redirect_submit"), {
            'new-redirect-from': "/from?",
            'new-redirect-to': "to!",
            'new-redirect-short-url': "true",
            'expiration-date': "Fri Jul 01 2016"
        })
        expected_response = repr("\xec\xb6\x18!|\x08Y\x05\xc6\x90'a?\xb4<\xfa")  # b'deleted done'
        form_contents = self.create_form("16928")
        response = self.send_post(self.request, form_contents)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)

    def test_delete_invalid_path(self):
        expected_response = repr('\x95\xb3dEV\xb4\x8a%\xf36m\x82\xb0\xe3\xb3I')  # b'fail'
        form_contents = self.create_form("999999")
        response = self.send_post(self.request, form_contents)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)
