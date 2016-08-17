from sync_base import SyncBaseTestCase


class AllTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, id):
        csrf_token = super(AllTestCase, self).get_csrf_token("/admin/sync")
        return {
            'csrf_token': csrf_token,
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_all(self):
        form_contents = self.create_form("yes")
        response = super(AllTestCase, self).send_post("/admin/sync/all", form_contents)
        assert b'<h3>Successfully Synced' in response.data