import re
from unit_tests import BaseTestCase


class EAnnouncementsSequentialTestCase(BaseTestCase):

    def __init__(self, methodName):
        super(EAnnouncementsSequentialTestCase, self).__init__(methodName)
        self.eaid = None
        self.request_type = ""
        self.request = ""

    def get_eaid(self, text):
        return re.search('<input(.*)id="new_eaid"(.*)value="(.+)"(/?)>', text).group(3)

    def create_form(self, title, eaid=None):
        to_return = {
            'title': title,
            'message': "This E-Announcement should never be seen by the public, I hope",
            'name': "Philip Gibbens",
            'email': "phg49389@bethel.edu",
            'first_date': '08-01-2017',
            'second_date': '08-05-2017',
            'banner_roles': 'STUDENT-CAS'
        }
        if eaid:
            to_return['e_announcement_id'] = eaid
        return to_return

    def test_sequence(self):
        # Get new form
        self.request_type = "GET"
        self.request = self.generate_url("new")
        expected_response = b'<form id="eannouncementform" action="/e-announcements/submit"'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

        # Submit the new form to create a new object
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"You've successfully created your E-Announcement. Once your E-Announcement has been approved,"
        response = self.send_post(self.request, self.create_form("First title"))
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)
        self.eaid = self.get_eaid(response.data)

        ###################################################################################
        ### The new submission goes to workflow; thus /edit and /duplicate should fail. ###
        ###################################################################################

        # Get edit form
        self.request_type = "GET"
        self.request = self.generate_url("edit", e_announcement_id=self.eaid)
        expected_response = b'<input type="hidden" name="e_announcement_id" id="e_announcement_id"'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertNotIn(expected_response, response.data, msg=failure_message)

        # Edit that new object
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"You've successfully edited your E-Announcement. Once your E-Announcement has been approved,"
        response = self.send_post(self.request, self.create_form("Second title", eaid=self.eaid))
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

        # Call the duplicate form to make sure it works
        self.request_type = "GET"
        self.request = self.generate_url("duplicate", e_announcement_id=self.eaid)
        expected_response = b'<form id="eannouncementform" action="/e-announcements/submit"'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertNotIn(expected_response, response.data, msg=failure_message)

        # Delete the new object
        self.request = self.generate_url("delete", e_announcement_id=self.eaid)
        expected_response = b'Your E-Announcements has been deleted. It will be removed from your'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)