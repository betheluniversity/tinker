from publish_base import PublishBaseTestCase


class IndexTestCase(PublishBaseTestCase):
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
        failure_message = '"GET /admin/publish-manager" didn\'t return the HTML code expected by ' + self.class_name + '.'
        expected_response = b'<h3>Here are the automated publishers</h3>'
        response = super(IndexTestCase, self).send_get("/admin/publish-manager")
        self.assertIn(expected_response, response.data, msg=failure_message)

