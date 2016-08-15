from sync_base import SyncBaseTestCase


class DataDefinitionTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, id):
        csrf_token = super(DataDefinitionTestCase, self).get_csrf_token("/admin/sync")
        return {
            'csrf_token': csrf_token,
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_datadefinition(self):
        form_contents = self.create_form("yes")
        response = super(DataDefinitionTestCase, self).send_post("/admin/sync/datadefinition", form_contents)
        assert b'<h3>Successfully Synced' in response.data