from e_announcements_base import EAnnouncementsBaseTestCase


class IndexTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        failure_message = '"GET /e-announcement" didn\'t return the HTML code expected by ' + self.class_name + '.'
        expected_response = b'Below is the list of E-Announcements you have access to edit. These are sorted by'
        response = super(IndexTestCase, self).send_get("/e-announcement")
        self.assertIn(expected_response, response.data, msg=failure_message)
