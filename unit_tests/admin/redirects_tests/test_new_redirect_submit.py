from redirects_base import RedirectsBaseTestCase


class NewRedirectSubmitTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(NewRedirectSubmitTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

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
        failure_message = 'Sending a valid new redirect to "POST /admin/redirect/new-redirect-submit" didn\'t succeed as it should have in ' + self.class_name + '.'
        expected_response = b'<Redirect /from? to to!>'
        form_contents = self.create_new_form_submission("from?", "to!")
        response = super(NewRedirectSubmitTestCase, self).send_post('/admin/redirect/new-redirect-submit', form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)
        # add an assertion that it got added to the database

    def test_new_redirect_submit_invalid_from(self):
        failure_message = 'Sending an invalid "from" to "POST /admin/redirect/new-redirect-submit" didn\'t fail as expected in ' + self.class_name + '.'
        expected_response = b'400 Bad Request'
        form_contents = self.create_new_form_submission(None, "to!")
        response = super(NewRedirectSubmitTestCase, self).send_post('/admin/redirect/new-redirect-submit', form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_new_redirect_submit_invalid_to(self):
        failure_message = 'Sending an invalid "to" to "POST /admin/redirect/new-redirect-submit" didn\'t fail as expected in ' + self.class_name + '.'
        expected_response = b'400 Bad Request'
        form_contents = self.create_new_form_submission("from?", None)
        response = super(NewRedirectSubmitTestCase, self).send_post('/admin/redirect/new-redirect-submit', form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)