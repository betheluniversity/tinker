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

    def create_form(self, title="First title", message="This E-Announcement should never be seen by the public, I hope",
                    first_date='08-01-2017', second_date='08-05-2017', banner_roles='STUDENT-CAS', eaid=None):
        to_return = {
            'title': title,
            'message': message,
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
        # Because the ID returned will always be different, we can't assertEqual; have to use the old assertIn
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"You've successfully created your E-Announcement. Once your E-Announcement has been approved,"
        form = self.create_form()
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)
        self.eaid = self.get_eaid(response.data)

    def submit_new_form_invalid(self):
        # Because a the form will have a different error every time, can't assertEqual on the same string.
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"There were errors with your form."
        arg_names = ['title', 'message', 'first_date', 'banner_roles']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: ""}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/new_form_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertIn(expected_response, response.data, msg=failure_message)

    def get_edit_form(self):
        self.request_type = "GET"
        self.request = self.generate_url("edit", e_announcement_id=self.eaid)
        expected_response = b'<input type="hidden" name="e_announcement_id" id="e_announcement_id"'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_valid(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"You've successfully edited your E-Announcement. Once your E-Announcement has been approved,"
        form = self.create_form(title="Second title", eaid=self.eaid)
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
        self.assertIn(expected_response, response.data, msg=failure_message)

    def delete_testing_object(self):
        self.request = self.generate_url("delete", e_announcement_id=self.eaid)
        expected_response = repr('\xcc\x01I5\xeb\xde\xf9{\x97\xf9)\xbe\xcd\x95\xa9"')
        # b'Your E-Announcements has been deleted. It will be removed from your'
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)

    def test_sequence(self):
        self.get_new_form()

        self.submit_new_form_valid()
        self.submit_new_form_invalid()

        self.get_edit_form()

        self.submit_edit_valid()

        self.get_duplicate_form()

        self.delete_testing_object()
