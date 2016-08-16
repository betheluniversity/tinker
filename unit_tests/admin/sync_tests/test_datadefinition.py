from sync_base import SyncBaseTestCase


class DataDefinitionTestCase(SyncBaseTestCase):
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

    def test_datadefinition(self):
        form_contents = self.create_form("yes")
        response = super(DataDefinitionTestCase, self).send_post("/admin/sync/datadefinition", form_contents)
        assert b'<h3>Successfully Synced' in response.data