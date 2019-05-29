import re

from testing_suite.integration_tests import IntegrationTestCase


class FacultyBioSequentialTestCase(IntegrationTestCase):

    def __init__(self, methodName):
        super(FacultyBioSequentialTestCase, self).__init__(methodName)
        self.request_type = ""
        self.request = ""
        self.fbid = ""
        self.form_arg_names = ['first', 'last', 'author_faculty', 'faculty_location', 'highlight', 'schools1', 'undergrad1',
                               'dept-chair1', 'adult-undergrad1', 'graduate1', 'lead-faculty1' 'seminary1', 'new-job-title1',
                               'email', 'started_at_bethel', 'school1', 'degree-earned1', 'year1', 'biography',
                               'courses', 'awards', 'publications', 'presentations', 'certificates', 'organizations',
                               'hobbies', 'areas', 'research_interests', 'teaching_specialty', 'quote', 'website']

    def get_faculty_bio_id(self, responseData):
        return re.search('id="faculty_bio_id".*value="(.+)"', responseData).group(1)

    def create_form(self, first='Philip', last='Gibbens', author_faculty='phg49389', location='St. Paul',
                    highlight='This is a testing Faculty Bio -- it should not be published.',
                    schools='College of Arts and Sciences', undergrad='Music', dept_chair='No', adult_undergrad='-select-',
                    graduate='-select-', seminary='-select-', job_title='Web Developer',
                    email='p-gibbens@bethel.edu', started_at_bethel='2011', school='Bethel University',
                    degree_earned='Jack of All Trades, M.N.', year='2016', biography='<p>asdf1</p>\r\n',
                    courses='<p>asdf2</p>\r\n', awards='<p>asdf3</p>\r\n', publications='<p>asdf4</p>\r\n',
                    presentations='<p>asdf5</p>\r\n', certificates='<p>asdf6</p>\r\n', organizations='<p>asdf7</p>\r\n',
                    hobbies='<p>asdf8</p>\r\n', areas='<p>asdf9</p>\r\n', research_interests='<p>asdf10</p>\r\n',
                    teaching_speciality='<p>asdf11</p>\r\n', quote='Arbitrarily compulsive, compulsively arbitrary.',
                    website='None.', fbid=None):

        to_return = {
            'image': '',
            'image_url': '',
            'first': first,
            'last': last,
            'author_faculty': author_faculty,
            'courseleaf_user': 'No',
            'faculty_location': location,
            'highlight': highlight,

            'num_jobs': '0',
            'num_new_jobs': '1',
            'schools1': schools,
            'undergrad1': undergrad,
            'dept-chair1': dept_chair,
            'adult-undergrad1': adult_undergrad,
            'graduate1': graduate,
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
        form_contents = self.create_form()
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)
        self.fbid = self.get_faculty_bio_id(response.data)

    def submit_new_form_all_invalid_types(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b'There were errors with your form'

        # Test all independent required fields
        required_vals = ['first', 'last', 'author_faculty', 'location', 'highlight', 'email', 'started_at_bethel']
        for index in range(len(required_vals)):
            bad_args = {required_vals[index]: ""}
            form = self.create_form(**bad_args)
            response = self.send_post(self.request, form)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/new_invalid_" + required_vals[index],
                                                            self.get_line_number())
            self.assertIn(expected_response, response.data, msg=failure_message)

    def get_edit_form(self):
        self.request_type = "GET"
        self.request = self.generate_url("edit", faculty_bio_id=self.fbid)
        expected_response = b'<input type="hidden" name="faculty_bio_id" id="faculty_bio_id"'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_valid(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b"You've successfully edited your bio. Your edits have been sent for approval but will be ready to"
        form_contents = self.create_form(fbid=self.fbid)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
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

        self.delete_testing_object()
