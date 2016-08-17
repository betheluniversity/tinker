from publish_base import PublishBaseTestCase


class PublishProgramFeedsReturnTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_publish_program_feeds_return(self):
        destination = "staging"  # or "production"
        response = super(PublishProgramFeedsReturnTestCase, self).send_get("/admin/publish-manager/program-feeds/" + destination)
        assert b'<h3>Publish Program Feeds</h3>' in response.data

        # <a href=\'/admin/publish-manager/program-feeds/staging\' class="button">Publish to Staging</a>\
        # <a href=\'/admin/publish-manager/program-feeds/production\' class="button">Publish to Production and Staging</a>' in response.data