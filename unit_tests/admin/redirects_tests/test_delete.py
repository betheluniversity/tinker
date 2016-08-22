from redirects_base import RedirectsBaseTestCase


class DeleteTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(DeleteTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    def create_form(self, from_path):
        return {
            'from_path': from_path
        }

    #######################
    ### Testing methods ###
    #######################

    def test_delete_valid(self):
        failure_message = 'Sending a valid delete request to "POST /admin/redirect/delete" didn\'t succeed when it should have in ' + self.class_name + '.'
        expected_response = b'delete'
        form_contents = self.create_form("/development")
        response = super(DeleteTestCase, self).send_post('/admin/redirect/delete', form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_delete_invalid_path(self):
        failure_message = 'Sending an invalid delete request to "POST /admin/redirect/delete" didn\'t fail as expected in ' + self.class_name + '.'
        expected_response = b'fail'
        form_contents = self.create_form("/from?")
        response = super(DeleteTestCase, self).send_post('/admin/redirect/delete', form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)