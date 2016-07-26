from sync_base import SyncBaseTestCase


class DataDefinitionTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = super(DataDefinitionTestCase, self).send_post("/admin/sync/datadefinition", {})
        assert b'<h3>Successfully Synced' in response.data