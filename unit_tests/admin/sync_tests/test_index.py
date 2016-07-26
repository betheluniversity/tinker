from sync_base import SyncBaseTestCase


class IndexTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = super(IndexTestCase, self).send_get("/admin/sync")
        assert b'<p>The sync data is contained in this <a target="_blank" href="https://github.com/betheluniversity/tinker/blob/master/tinker/admin/sync/sync_metadata.py">file</a>. You can sync a specific metadata set, data definition, or sync all.</p>' in response.data