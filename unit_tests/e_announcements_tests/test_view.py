from e_announcements_base import EAnnouncementsBaseTestCase


class ViewTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ViewTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_view(self):
        # The id may need to get changed someday if this e-announcement gets deleted
        id_to_test = "12f336eb8c58651305d79299154d15ff"
        failure_message = '"GET /e-announcement/view/%s" didn\'t return the HTML code expected by ' % id_to_test + self.class_name + '.'
        expected_response = b'<h5>First Date</h5>'
        response = super(ViewTestCase, self).send_get("/e-announcement/view/" + id_to_test)
        self.assertIn(expected_response, response.data, msg=failure_message)
