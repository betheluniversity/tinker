from sync_base import SyncBaseTestCase


class AllTestCase(SyncBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(AllTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "POST /admin/sync/all"

    def create_form(self, id):
        return {
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_all(self):
        expected_response = b'<h3>Successfully Synced'
        form_contents = self.create_form("yes")
        response = super(AllTestCase, self).send_post("/admin/sync/all", form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)