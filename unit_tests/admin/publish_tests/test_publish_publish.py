from publish_base import PublishBaseTestCase


class PublishPublishTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(PublishPublishTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /admin/publish-manager/publish/"

    #######################
    ### Testing methods ###
    #######################

    def test_publish_publish(self):
        destination = "staging"  # or "production"
        publish_type = "page"
        publish_id = "a7404faa8c58651375fc4ed23d7468d5"
        failure_message = '"GET /admin/publish-manager/publish/%s/%s/%s" didn\'t return the HTML code expected by ' % (destination, publish_type, publish_id) \
                          + self.class_name + '.'
        response = super(PublishPublishTestCase, self).send_get("/admin/publish-manager/publish/" + destination + "/" + publish_type + "/" + publish_id)
        publishing = b'Publishing. . .' in response.data
        already_exists = b'This asset already exists in the publish queue' in response.data
        expected_response = "'Publishing. . .' or 'This asset already exists in the publish queue'"
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertTrue(publishing or already_exists, msg=failure_message)
