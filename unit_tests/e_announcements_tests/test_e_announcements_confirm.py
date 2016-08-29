from e_announcements_base import EAnnouncementsBaseTestCase


class ConfirmTestCase(EAnnouncementsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ConfirmTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /e-announcement/confirm"

    #######################
    ### Testing methods ###
    #######################

    def test_confirm(self):
        expected_response = b"You've successfully created your E-Announcement. Once your E-Announcement has been approved,"
        response = super(ConfirmTestCase, self).send_get("/e-announcement/confirm")
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)
