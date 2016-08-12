from redirects_Base import RedirectsBaseTestCase


class DeleteTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, from_path):
        csrf_token = super(DeleteTestCase, self).get_csrf_token('/admin/redirect')
        return {
            'csrf_token': csrf_token,
            'from_path': from_path
        }

    #######################
    ### Testing methods ###
    #######################

    def test_delete_valid(self):
        form_contents = self.create_form("/development")
        response = super(DeleteTestCase, self).send_post('/admin/redirect/delete', form_contents)
        assert b'delete' in response.data

    def test_delete_invalid_path(self):
        form_contents = self.create_form("/from?")
        response = super(DeleteTestCase, self).send_post('/admin/redirect/delete', form_contents)
        assert b'fail' in response.data