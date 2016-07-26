from redirects_base import RedirectsBaseTestCase


class DeleteTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_delete_valid(self):
        form_contents = {'from_path': "/development"}
        response = super(DeleteTestCase, self).send_post('/admin/redirect/delete', form_contents)
        assert b'delete' in response.data

    def test_delete_invalid_path(self):
        form_contents = {'from_path': "from?"}
        response = super(DeleteTestCase, self).send_post('/admin/redirect/delete', form_contents)
        print "Redirects/DeleteTestCase/Invalid:", response.data
        assert b'fail' in response.data