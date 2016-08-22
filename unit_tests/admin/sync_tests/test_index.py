from sync_base import SyncBaseTestCase


class IndexTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        failure_message = '"GET /admin/sync" didn\'t return the HTML code expected by ' + self.class_name + '.'
        expected_response = b'You can sync a specific metadata set, data definition, or sync all.</p>'
        response = super(IndexTestCase, self).send_get("/admin/sync")
        self.assertIn(expected_response, response.data, msg=failure_message)