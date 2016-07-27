from sync_base import SyncBaseTestCase


class MetadataTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, id):
        csrf_token = super(MetadataTestCase, self).get_csrf_token("/admin/sync")
        return {
            'csrf_token': csrf_token,
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_metadata(self):
        form_contents = self.create_form("yes")
        response = super(MetadataTestCase, self).send_post("/admin/sync/metadata", form_contents)
        assert b'<h3>Successfully Synced' in response.data