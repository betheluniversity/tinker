import re
import time
import tinker
import unittest


class FacultyBioSequentialTestCase(unittest.TestCase):

    def setUp(self):
        tinker.app.testing = True
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        self.app = tinker.app.test_client()
        self.faculty_bio_id = None
        self.class_name = self.__class__.__name__

    def send_post(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True)

    def send_get(self, url):
        return self.app.get(url, follow_redirects=True)

    def get_faculty_bio_id(self, responseData):
        return re.search('id="faculty_bio_id".*value="(.+)"', responseData).group(1)

    def create_form_submission(self, f_b_id, job_title):
        return {
            'faculty_bio_id': f_b_id,
            'image_url': '',
            'first': 'Philip',
            'last': 'Gibbens',
            'author': 'phg49389',
            'num_jobs': '0',
            'num_new_jobs': '1',
            'schools1': 'Bethel University',
            'graduate1': 'None',
            'seminary1': 'None',
            'undergrad1': 'None',
            'adult-undergrad1': 'None',
            'new-job-title1': job_title,
            'email': 'phg49389@bethel.edu',
            'started_at_bethel': '2011',
            'heading': 'Areas of expertise',
            'teaching_specialty': '',
            'research_interests': '',
            'areas': 'asdf',
            'num_degrees': '1',
            'school1': 'Bethel University',
            'degree-earned1': 'B.S. of Computer Science',
            'year1': '2016',
            'biography': '<p>asdf</p>\r\n',
            'courses': '<p>asdf</p>\r\n',
            'awards': '<p>adsf</p>\r\n',
            'publications': '<p>asdf</p>\r\n',
            'presentations': '<p>asdf</p>\r\n',
            'certificates': '<p>asdf</p>\r\n',
            'organizations': '<p>asdf</p>\r\n',
            'hobbies': '<p>asdf</p>\r\n',
            'quote': 'Arbitrarily compulsive, compulsively arbitrary.',
            'website': 'None.',
        }

    def test_sequence(self):
        # Get a new form to fill out
        failure_message = '"GET /faculty-bio/new" didn\'t return the HTML code expected by ' + self.class_name + '.'
        expected_response = b'<form id="facultybioform" action="/faculty-bio/submit" method="post">'
        response = self.send_get("/faculty-bio/new")
        self.assertIn(expected_response, response.data, msg=failure_message)

        # Send the form submission to create it in Cascade
        failure_message = 'Sending a valid new submission to "POST /faculty-bio/submit" didn\'t succeed as expected by ' + self.class_name + '.'
        expected_response = b"You've successfully created a new bio. Your brand new bio has been sent for approval but will be"
        form_contents = self.create_form_submission("", "Web Developer")
        response = self.send_post("/faculty-bio/submit", form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)
        self.faculty_bio_id = self.get_faculty_bio_id(response.data)

        # Open up the new bio to edit it
        failure_message = '"GET /faculty-bio/edit/%s" didn\'t return the HTML code expected by ' % self.faculty_bio_id + self.class_name + '.'
        expected_response = b'<form id="facultybioform" action="/faculty-bio/submit" method="post">'
        response = self.send_get("/faculty-bio/edit/" + self.faculty_bio_id)
        self.assertIn(expected_response, response.data, msg=failure_message)

        # Send the edited form to update the bio
        failure_message = 'Sending a valid edit submission to "POST /faculty-bio/submit" didn\'t succeed as expected by ' + self.class_name + '.'
        expected_response = b"You've successfully edited your bio. Your edits have been sent for approval but will be ready to"
        form_contents = self.create_form_submission(self.faculty_bio_id, "Web Developers")
        response = self.send_post("/faculty-bio/submit", form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)

        # Delete the new bio to make sure these tests don't bloat Cascade
        time.sleep(20)
        failure_message = '"GET /faculty-bio/delete/%s" didn\'t return the HTML code expected by ' % self.faculty_bio_id + self.class_name + '.'
        expected_response = b'Your faculty bio has been deleted. It will be removed from your'
        response = self.send_get("/faculty-bio/delete/" + self.faculty_bio_id)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def tearDown(self):
        pass
