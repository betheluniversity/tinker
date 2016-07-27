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
        response = super(PublishPublishTestCase, self).send_get("/admin/publish-manager/publish/" + destination + "/" + publish_type + "/" + publish_id)
        assert b'This asset already exists in the publish queue' in response.data or b'Publishing. . .' in response.data