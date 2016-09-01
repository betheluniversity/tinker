from redirects_base import RedirectsBaseTestCase


class NewRedirectSubmitTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(NewRedirectSubmitTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "POST /admin/redirect/new-redirect-submit"

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
        response = super(NewRedirectSubmitTestCase, self).send_post('/admin/redirect/new-redirect-submit', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)
        # add an assertion that it got added to the database

    def test_new_redirect_submit_invalid_from(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_new_form_submission(None, "to!")
        response = super(NewRedirectSubmitTestCase, self).send_post('/admin/redirect/new-redirect-submit', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_new_redirect_submit_invalid_to(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_new_form_submission("from?", None)
        response = super(NewRedirectSubmitTestCase, self).send_post('/admin/redirect/new-redirect-submit', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)