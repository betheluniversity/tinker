from e_announcements_base import EAnnouncementsBaseTestCase


class ConfirmTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_confirm(self):
        response = super(ConfirmTestCase, self).send_get("/e-announcement/confirm")
        assert b'Once your E-Announcement has been approved, it will appear on your Tinker' in response.data
