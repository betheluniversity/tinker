import re
import time
from unit_tests import BaseTestCase


class FacultyBioSequentialTestCase(BaseTestCase):

    def __init__(self, methodName):
        super(FacultyBioSequentialTestCase, self).__init__(methodName)
        self.request_type = ""
        self.request = ""
        self.fbid = ""
        self.form_arg_names = ['first', 'last', 'author', 'faculty_location', 'highlight', 'schools1', 'undergrad1',
                               'adult-undergrad1', 'graduate1', 'seminary1', 'new-job-title1',
                               'email', 'started_at_bethel', 'school1', 'degree-earned1', 'year1', 'biography',
                               'courses', 'awards', 'publications', 'presentations', 'certificates', 'organizations',
                               'hobbies', 'areas', 'research_interests', 'teaching_specialty', 'quote', 'website']
        self.valid_form_values = ['Philip', 'Gibbens', 'phg49389', 'St. Paul',
                                  "A great magazine for the dentist's office", 'Bethel University', 'None',
                                  'None', 'None', 'None', "Web Developer", 'phg49389@bethel.edu', '2011',
                                  'Bethel University',
                                  'B.S. of Computer Science', '2016',
                                  '<p>asdf1</p>\r\n', '<p>asdf2</p>\r\n', '<p>asdf3</p>\r\n', '<p>asdf4</p>\r\n',
                                  '<p>asdf5</p>\r\n', '<p>asdf6</p>\r\n', '<p>asdf7</p>\r\n', '<p>asdf8</p>\r\n',
                                  '<p>asdf9</p>\r\n', '<p>fdsa1</p>\r\n', '<p>fdsa2</p>\r\n',
                                  'Arbitrarily compulsive, compulsively arbitrary.', 'None.']

    def get_faculty_bio_id(self, responseData):
        return re.search('id="faculty_bio_id".*value="(.+)"', responseData).group(1)

    def create_form(self, first, last, author, location, highlight, schools, undergrad, adult_undergrad, graduate,
                    seminary, job_title, email, started_at_bethel, school, degree_earned, year, biography, courses,
                    awards, publications, presentations, certificates, organizations, hobbies, areas,
                    research_interests, teaching_speciality, quote, website, fbid=None):

        to_return = {
            'image': '',
            'image_url': '',
            'first': first,
            'last': last,
            'author': author,
            'faculty_location': location,
            'highlight': highlight,

            'num_jobs': '0',
            'num_new_jobs': '1',
            'schools1': schools,
            'undergrad1': undergrad,
            'dept-chair1': 'No',
            'adult-undergrad1': adult_undergrad,
            'program-director1': 'No',
            'graduate1': graduate,
            'lead-faculty1': 'Other',
            'seminary1': seminary,
            'new-job-title1': job_title,

            'email': email,
            'started_at_bethel': started_at_bethel,

            'num_degrees': '1',
            'school1': school,
            'degree-earned1': degree_earned,
            'year1': year,

            'biography': biography,
            'courses': courses,
            'awards': awards,
            'publications': publications,
            'presentations': presentations,
            'certificates': certificates,
            'organizations': organizations,
            'hobbies': hobbies,
            'areas': areas,
            'research_interests': research_interests,
            'teaching_specialty': teaching_speciality,
            'quote': quote,
            'website': website
        }
        if fbid:
            to_return['faculty_bio_id'] = fbid
        else:
            to_return['faculty_bio_id'] = ""
        return to_return

    def get_new_form(self):
        self.request_type = "GET"
        self.request = self.generate_url("new")
        expected_response = b'<form id="facultybioform" action="/faculty-bios/submit" method="post" enctype="multipart/form-data">'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_new_form_valid(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"You've successfully created a new bio. Your brand new bio has been sent for approval but will be"
        form_contents = self.create_form(*self.valid_form_values)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)
        self.fbid = self.get_faculty_bio_id(response.data)

    def submit_new_form_all_invalid_types(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b'There were errors with your form'
        for index in range(len(self.form_arg_names)):
            invalid_form_array = list(self.valid_form_values)
            invalid_form_array[index] = ""
            form = self.create_form(*invalid_form_array)
            response = self.send_post(self.request, form)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/new_invalid_" + self.form_arg_names[
                                                                index],
                                                            self.get_line_number())
            self.assertIn(expected_response, response.data, msg=failure_message)

    def get_edit_form(self):
        self.request_type = "GET"
        self.request = self.generate_url("edit", faculty_bio_id=self.fbid)
        expected_response = b'You recently made edits to your bio and are currently pending approval.'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_valid(self):
        print "FBID =", self.fbid
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"You've successfully edited your bio. Your edits have been sent for approval but will be ready to"
        form_contents = self.create_form(*self.valid_form_values, fbid=self.fbid)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_all_invalid_types(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b'There were errors with your form'
        for index in range(len(self.form_arg_names)):
            invalid_form_array = list(self.valid_form_values)
            invalid_form_array[index] = ""
            form = self.create_form(*invalid_form_array)
            response = self.send_post(self.request, form)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/edit_invalid_" + self.form_arg_names[
                                                                index],
                                                            self.get_line_number())
            self.assertIn(expected_response, response.data, msg=failure_message)

    def delete_testing_object(self):
        self.request_type = "GET"
        self.request = self.generate_url("delete", faculty_bio_id=self.fbid)
        expected_response = b'Your faculty bio has been deleted. It will be removed from your'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_sequence(self):
        self.get_new_form()

        self.submit_new_form_valid()
        self.submit_new_form_all_invalid_types()

        self.get_edit_form()

        self.submit_edit_valid()
        self.submit_edit_all_invalid_types()

        self.delete_testing_object()
