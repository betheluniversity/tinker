from unit_tests import BaseTestCase


class ConfirmTestCase(BaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ConfirmTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = self.generate_url("confirm", status='new')

    #######################
    ### Testing methods ###
    #######################

    def test_confirm(self):
        expected_response = repr('\x0e\xcd\x1c\xdb+yg\x18\xd1\xd1U\xe7\xac\x85V$')
        # b"You've successfully created your E-Announcement. Once your E-Announcement has been approved,"
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)
