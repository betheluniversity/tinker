from publish_base import PublishBaseTestCase


class PublishPublishTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(PublishPublishTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

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
        self.assertTrue(publishing or already_exists, msg=failure_message)
