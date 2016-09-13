from unit_tests import BaseTestCase


class SubmitTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SubmitTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "POST"
        self.request = self.generate_url("submit")

    def create_form(self, name, title, banner_roles, first_date, message, second_date, email):
        return {
            'name': name,
            'title': title,
            'banner_roles': banner_roles,
            'first_date': first_date,
            'message': message,
            'second_date': second_date,
            'email': email
        }

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        expected_response = b'Once your E-Announcement has been approved, it'
        form_contents = self.create_form("Philip Gibbens", "First title", "STUDENT-CAS", "08-01-2017", "This E-Announcement should never be seen by the public, I hope", "08-05-2017", "phg49389@bethel.edu")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_name(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form(None, "First title", "STUDENT-CAS", "08-01-2017", "This E-Announcement should never be seen by the public, I hope", "08-05-2017", "phg49389@bethel.edu")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_title(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("Philip Gibbens", None, "STUDENT-CAS", "08-01-2017", "This E-Announcement should never be seen by the public, I hope", "08-05-2017", "phg49389@bethel.edu")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_banner_roles(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("Philip Gibbens", "First title", None, "08-01-2017", "This E-Announcement should never be seen by the public, I hope", "08-05-2017", "phg49389@bethel.edu")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_first_date(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("Philip Gibbens", "First title", "STUDENT-CAS", None, "This E-Announcement should never be seen by the public, I hope", "08-05-2017", "phg49389@bethel.edu")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_message(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("Philip Gibbens", "First title", "STUDENT-CAS", "08-01-2017", None, "08-05-2017", "phg49389@bethel.edu")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_second_date(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("Philip Gibbens", "First title", "STUDENT-CAS", "08-01-2017", "This E-Announcement should never be seen by the public, I hope", None, "phg49389@bethel.edu")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_email(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("Philip Gibbens", "First title", "STUDENT-CAS", "08-01-2017", "This E-Announcement should never be seen by the public, I hope", "08-05-2017", None)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
