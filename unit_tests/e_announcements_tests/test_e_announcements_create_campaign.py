from e_announcements_base import EAnnouncementsBaseTestCase


class CreateCampaignTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CreateCampaignTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_create_campaign(self):
        failure_message = '"GET /e-announcement/create_campaign" didn\'t fail as expected by ' + self.class_name + '.'
        expected_response = b'401 UNAUTHORIZED'
        response = super(CreateCampaignTestCase, self).send_get("/e-announcement/create_campaign")
        # Per Eric, for now we're leaving this endpoint untested. This is because this endpoint will create a Carlyle
        # campaign, but wouldn't be able to send it, so it would just pile up a bunch of unused campaigns.
        self.assertIn(expected_response, str(response), msg=failure_message)
