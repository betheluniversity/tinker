from . import SyncBaseTestCase


class MetadataTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = self.send_post("/admin/sync/metadata", {})
        assert b'<h3>Successfully Synced' in response.data