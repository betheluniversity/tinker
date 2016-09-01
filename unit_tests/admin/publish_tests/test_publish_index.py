from unit_tests import BaseTestCase


class IndexTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /admin/publish-manager"

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        expected_response = b'<p>Blocks that are published publish out each page in the relationships tab.</p>'
        response = super(IndexTestCase, self).send_get("/admin/publish-manager")
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

