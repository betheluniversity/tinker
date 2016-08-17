from sync_base import SyncBaseTestCase


class IndexTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /admin/sync" didn\'t return the HTML code expected by ' + class_name + '.'
        response = super(IndexTestCase, self).send_get("/admin/sync")
        self.assertIn(b'<p>The sync data is contained in this <a target="_blank" href="https://github.com/betheluniversity/tinker/blob/master/tinker/admin/sync/sync_metadata.py">file</a>. You can sync a specific metadata set, data definition, or sync all.</p>',
                      response.data, msg=failure_message)