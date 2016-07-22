from . import EAnnouncementsBaseTestCase


class IndexTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_delete_valid(self):
        block_id = "asdf"
        response = self.send_get("/e-announcement/delete/" + block_id)
        print response.data
        assert b'<p>Below is the list of E-Announcements you have access to edit.' in response.data
