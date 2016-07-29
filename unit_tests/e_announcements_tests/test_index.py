from e_announcements_base import EAnnouncementsBaseTestCase


class IndexTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index_valid(self):
        response = self.send_get("/e-announcement")
        print response.data
        assert b'<p>Below is the list of E-Announcements you have access to edit.' in response.data
