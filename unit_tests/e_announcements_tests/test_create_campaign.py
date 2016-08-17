from e_announcements_base import EAnnouncementsBaseTestCase


class CreateCampaignTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_create_campaign(self):
        response = super(CreateCampaignTestCase, self).send_get("/e-announcement/create_campaign")
        # Per Eric, for now we're leaving this endpoint untested. This is because this endpoint will create a Carlyle
        # campaign, but wouldn't be able to send it, so it would just pile up a bunch of unused campaigns.
        assert b'401 UNAUTHORIZED' in str(response)
