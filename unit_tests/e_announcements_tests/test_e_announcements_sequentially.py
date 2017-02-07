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

    def create_form(self, title, message, name, email, first_date, second_date, banner_roles, eaid=None):
        to_return = {
            'title': title,
            'message': message,
            'name': name,
            'email': email,
            'first_date': first_date,
            'second_date': second_date,
            'banner_roles': banner_roles
        }
        if eaid:
            to_return['e_announcement_id'] = eaid
        return to_return

    def get_new_form(self):
        self.request_type = "GET"
        self.request = self.generate_url("new")
        expected_response = b'<form id="eannouncementform" action="/e-announcements/submit"'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_new_form_valid(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"You've successfully created your E-Announcement. Once your E-Announcement has been approved,"
        form = self.create_form("First title", "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", "phg49389@bethel.edu", '08-01-2017', '08-05-2017', 'STUDENT-CAS')
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)
        self.eaid = self.get_eaid(response.data)

    def submit_new_form_invalid_title(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form(None, "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", "phg49389@bethel.edu", '08-01-2017', '08-05-2017', 'STUDENT-CAS')
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_new_form_invalid_message(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("First title", None,
                                "Philip Gibbens", "phg49389@bethel.edu", '08-01-2017', '08-05-2017', 'STUDENT-CAS')
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_new_form_invalid_name(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("First title", "This E-Announcement should never be seen by the public, I hope",
                                None, "phg49389@bethel.edu", '08-01-2017', '08-05-2017', 'STUDENT-CAS')
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_new_form_invalid_email(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("First title", "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", None, '08-01-2017', '08-05-2017', 'STUDENT-CAS')
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_new_form_invalid_first_date(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("First title", "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", "phg49389@bethel.edu", None, '08-05-2017', 'STUDENT-CAS')
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_new_form_invalid_second_date(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("First title", "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", "phg49389@bethel.edu", '08-01-2017', '08-05-2016', 'STUDENT-CAS')
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_new_form_invalid_banner_roles(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("First title", "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", "phg49389@bethel.edu", '08-01-2017', '08-05-2017', None)
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def get_edit_form(self):
        self.request_type = "GET"
        self.request = self.generate_url("edit", e_announcement_id=self.eaid)
        expected_response = b'<input type="hidden" name="e_announcement_id" id="e_announcement_id"'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertNotIn(expected_response, response.data, msg=failure_message)

    def submit_edit_valid(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"You've successfully edited your E-Announcement. Once your E-Announcement has been approved,"
        form = self.create_form("Second title", "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", "phg49389@bethel.edu", '08-01-2017', '08-05-2017', 'STUDENT-CAS',
                                eaid=self.eaid)
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_invalid_title(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form(None, "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", "phg49389@bethel.edu", '08-01-2017', '08-05-2017', 'STUDENT-CAS',
                                eaid=self.eaid)
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_invalid_message(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("Second title", None,
                                "Philip Gibbens", "phg49389@bethel.edu", '08-01-2017', '08-05-2017', 'STUDENT-CAS',
                                eaid=self.eaid)
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_invalid_name(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("Second title", "This E-Announcement should never be seen by the public, I hope",
                                None, "phg49389@bethel.edu", '08-01-2017', '08-05-2017', 'STUDENT-CAS',
                                eaid=self.eaid)
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_invalid_email(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("Second title", "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", None, '08-01-2017', '08-05-2017', 'STUDENT-CAS',
                                eaid=self.eaid)
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_invalid_first_date(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("Second title", "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", "phg49389@bethel.edu", None, '08-05-2017', 'STUDENT-CAS',
                                eaid=self.eaid)
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_invalid_second_date(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("Second title", "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", "phg49389@bethel.edu", '08-01-2017', '08-05-2016', 'STUDENT-CAS',
                                eaid=self.eaid)
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_invalid_banner_roles(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        form = self.create_form("Second title", "This E-Announcement should never be seen by the public, I hope",
                                "Philip Gibbens", "phg49389@bethel.edu", '08-01-2017', '08-05-2017', None,
                                eaid=self.eaid)
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def get_duplicate_form(self):
        self.request_type = "GET"
        self.request = self.generate_url("duplicate", e_announcement_id=self.eaid)
        expected_response = b'<form id="eannouncementform" action="/e-announcements/submit"'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertNotIn(expected_response, response.data, msg=failure_message)

    def delete_testing_object(self):
        self.request = self.generate_url("delete", e_announcement_id=self.eaid)
        expected_response = b'Your E-Announcements has been deleted. It will be removed from your'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_sequence(self):
        self.get_new_form()

        self.submit_new_form_valid()
        self.submit_new_form_invalid_title()
        self.submit_new_form_invalid_message()
        self.submit_new_form_invalid_name()
        self.submit_new_form_invalid_email()
        self.submit_new_form_invalid_first_date()
        self.submit_new_form_invalid_second_date()
        self.submit_new_form_invalid_banner_roles()

        self.get_edit_form()

        self.submit_edit_valid()
        self.submit_edit_invalid_title()
        self.submit_edit_invalid_message()
        self.submit_edit_invalid_name()
        self.submit_edit_invalid_email()
        self.submit_edit_invalid_first_date()
        self.submit_edit_invalid_second_date()
        self.submit_edit_invalid_banner_roles()

        self.get_duplicate_form()

        self.delete_testing_object()
