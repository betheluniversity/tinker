from redirects_base import RedirectsBaseTestCase


class DeleteTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, from_path):
        return {
            'from_path': from_path
        }

    #######################
    ### Testing methods ###
    #######################

    def test_delete_valid(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = 'Sending a valid delete request to "POST /admin/redirect/delete" didn\'t succeed when it should have in ' + class_name + '.'
        form_contents = self.create_form("/development")
        response = super(DeleteTestCase, self).send_post('/admin/redirect/delete', form_contents)
        self.assertIn(b'delete', response.data, msg=failure_message)

    def test_delete_invalid_path(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = 'Sending an invalid delete request to "POST /admin/redirect/delete" didn\'t fail as expected in ' + class_name + '.'
        form_contents = self.create_form("/from?")
        response = super(DeleteTestCase, self).send_post('/admin/redirect/delete', form_contents)
        self.assertIn(b'fail', response.data, msg=failure_message)