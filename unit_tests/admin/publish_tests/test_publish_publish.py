from . import PublishBaseTestCase


class PublishPublishTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_publish_publish(self):
        destination = "staging"  # or "production"
        publish_type = "yes"
        publish_id = "no"
        response = self.send_get("/admin/publish-manager/publish/" + destination + "/" + publish_type + "/" + publish_id)
        assert b'<h3>Publish Program Feeds</h3>\
        \
        <a href=\'/admin/publish-manager/program-feeds/staging\' class="button">Publish to Staging</a>\
        <a href=\'/admin/publish-manager/program-feeds/production\' class="button">Publish to Production and Staging</a>' in response.data