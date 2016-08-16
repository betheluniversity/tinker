from e_announcements_base import EAnnouncementsBaseTestCase


class ViewTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_view(self):
        # The id may need to get changed someday if this e-announcement gets deleted
        response = super(ViewTestCase, self).send_get("/e-announcement/view/12f336eb8c58651305d79299154d15ff")
        assert b'<h5>First Date</h5>' in response.data
