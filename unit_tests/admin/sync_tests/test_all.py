from . import SyncBaseTestCase


class AllTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = self.send_post("/admin/sync/all", {})
        assert b'<h3>Successfully Synced' in response.data