from publish_base import PublishBaseTestCase


class PublishProgramFeedsTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_publish_program_feeds(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"/admin/publish-manager/program-feeds" didn\'t return the HTML code expected by ' + class_name + '.'
        response = super(PublishProgramFeedsTestCase, self).send_get("/admin/publish-manager/program-feeds")
        self.assertIn(b'<h3>Publish Program Feeds</h3>', response.data, msg=failure_message)

        # <a href=\'/admin/publish-manager/program-feeds/staging\' class="button">Publish to Staging</a>\
        # <a href=\'/admin/publish-manager/program-feeds/production\' class="button">Publish to Production and Staging</a>' in response.data