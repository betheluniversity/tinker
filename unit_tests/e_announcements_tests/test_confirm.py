from e_announcements_base import EAnnouncementsBaseTestCase


class ConfirmTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ConfirmTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_confirm(self):
        failure_message = '"GET /e-announcement/confirm" didn\'t return the HTML code expected by ' + self.class_name + '.'
        expected_response = b"You've successfully created your E-Announcement. Once your E-Announcement has been approved,"
        response = super(ConfirmTestCase, self).send_get("/e-announcement/confirm")
        self.assertIn(expected_response, response.data, msg=failure_message)
