from e_announcements_base import EAnnouncementsBaseTestCase


class IndexTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /e-announcement" didn\'t return the HTML code expected by ' + class_name + '.'
        response = super(IndexTestCase, self).send_get("/e-announcement")
        self.assertIn(b'<p>Below is the list of E-Announcements you have access to edit.',
                      response.data, msg=failure_message)
