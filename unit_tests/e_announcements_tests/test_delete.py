from e_announcements_base import EAnnouncementsBaseTestCase


class IndexTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_delete_valid(self):
        block_id = "asdf"
        response = super(IndexTestCase, self).send_get("/e-announcement/delete/" + block_id)
        assert b'<p>Below is the list of E-Announcements you have access to edit.' in response.data
