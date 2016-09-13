from unit_tests import BaseTestCase


class NewRedirectSubmitTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(NewRedirectSubmitTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "POST"
        self.request = self.generate_url("new_redirect_submit")

    def create_form(self, new-redirect-from, short-url, expiration-date, new-redirect-to):
        return {
            'new-redirect-from': new-redirect-from,
            'short-url': short-url,
            'expiration-date': expiration-date,
            'new-redirect-to': new-redirect-to
        }

    #######################
    ### Testing methods ###
    #######################

    def test_new_redirect_submit_valid(self):
        expected_response = b'deleted'
        form_contents = self.create_form("from?", "on", "Fri Jul 01 2016", "to!")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_new_redirect_submit_invalid_new-redirect-from(self):
        expected_response = b'fail'
        form_contents = self.create_form(None, "on", "Fri Jul 01 2016", "to!")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_new_redirect_submit_invalid_short-url(self):
        expected_response = b'fail'
        form_contents = self.create_form("from?", None, "Fri Jul 01 2016", "to!")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_new_redirect_submit_invalid_expiration-date(self):
        expected_response = b'fail'
        form_contents = self.create_form("from?", "on", None, "to!")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_new_redirect_submit_invalid_new-redirect-to(self):
        expected_response = b'fail'
        form_contents = self.create_form("from?", "on", "Fri Jul 01 2016", None)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
