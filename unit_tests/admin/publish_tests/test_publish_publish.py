from publish_base import PublishBaseTestCase


class PublishPublishTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_publish_publish(self):
        destination = "staging"  # or "production"
        publish_type = "page"
        publish_id = "a7404faa8c58651375fc4ed23d7468d5"
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /admin/publish-manager/publish/%s/%s/%s" didn\'t return the HTML code expected by ' % (destination, publish_type, publish_id) \
                          + class_name + '.'
        response = super(PublishPublishTestCase, self).send_get("/admin/publish-manager/publish/" + destination + "/" + publish_type + "/" + publish_id)
        self.assertIn(b'This asset already exists in the publish queue', response.data, msg=failure_message)
        # This used to be an either/or assertion, but to do human-readable messages, I can only do one :(
        # self.assertIn(b'Publishing. . .', response.data, msg=failure_message)
