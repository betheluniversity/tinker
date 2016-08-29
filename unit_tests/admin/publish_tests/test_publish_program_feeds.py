from publish_base import PublishBaseTestCase


class PublishProgramFeedsTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(PublishProgramFeedsTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_publish_program_feeds(self):
        failure_message = '"/admin/publish-manager/program-feeds" didn\'t return the HTML code expected by ' \
                          + self.class_name + '.'
        expected_response = b'<h3 class="subtitle">Publish Program Feeds</h3>'
        response = super(PublishProgramFeedsTestCase, self).send_get("/admin/publish-manager/program-feeds")
        self.assertIn(expected_response, response.data, msg=failure_message)