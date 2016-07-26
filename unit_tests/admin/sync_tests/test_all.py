from sync_base import SyncBaseTestCase


class AllTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = super(AllTestCase, self).send_post("/admin/sync/all", {})
        assert b'<h3>Successfully Synced' in response.data