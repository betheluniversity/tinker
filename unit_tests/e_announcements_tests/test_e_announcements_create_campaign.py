from e_announcements_base import EAnnouncementsBaseTestCase


class CreateCampaignTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CreateCampaignTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /e-announcement/create_campaign"

    #######################
    ### Testing methods ###
    #######################

    def test_create_campaign(self):
        expected_response = b'401 UNAUTHORIZED'
        response = super(CreateCampaignTestCase, self).send_get("/e-announcement/create_campaign")
        # Per Eric, for now we're leaving this endpoint untested. This is because this endpoint will create a Carlyle
        # campaign, but wouldn't be able to send it, so it would just pile up a bunch of unused campaigns.
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, str(response), msg=failure_message)
