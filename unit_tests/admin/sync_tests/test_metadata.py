from sync_base import SyncBaseTestCase


class MetadataTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, id):
        return {
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_metadata(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = 'Sending a valid submission to "POST /admin/sync/metadata" didn\'t succeed as expected by ' + class_name + '.'
        form_contents = self.create_form("yes")
        response = super(MetadataTestCase, self).send_post("/admin/sync/metadata", form_contents)
        self.assertIn(b'<h3>Successfully Synced', response.data, msg=failure_message)