from sync_base import SyncBaseTestCase


class MetadataTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = super(MetadataTestCase, self).send_post("/admin/sync/metadata", {})
        assert b'<h3>Successfully Synced' in response.data