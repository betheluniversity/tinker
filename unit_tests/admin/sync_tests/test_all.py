from sync_base import SyncBaseTestCase


class AllTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(AllTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    def create_form(self, id):
        return {
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_all(self):
        failure_message = 'Sending a valid submission to "POST /admin/sync/all" didn\'t succeed as expected by ' + self.class_name + '.'
        expected_response = b'<h3>Successfully Synced'
        form_contents = self.create_form("yes")
        response = super(AllTestCase, self).send_post("/admin/sync/all", form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)