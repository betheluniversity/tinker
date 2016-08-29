from redirects_base import RedirectsBaseTestCase


class DeleteTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(DeleteTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "POST /admin/redirect/delete"

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
        response = super(DeleteTestCase, self).send_post('/admin/redirect/delete', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_delete_invalid_path(self):
        expected_response = b'fail'
        form_contents = self.create_form("/from?")
        response = super(DeleteTestCase, self).send_post('/admin/redirect/delete', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)