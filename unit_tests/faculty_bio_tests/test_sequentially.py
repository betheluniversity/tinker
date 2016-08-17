import re
import time
import tinker
import unittest


class SequentialTestCase(unittest.TestCase):

    def setUp(self):
        self.app = tinker.app.test_client()
        self.csrf_token = None
        self.faculty_bio_id = None

    def send_post(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True)

    def send_get(self, url):
        return self.app.get(url, follow_redirects=True)

    def get_csrf_token(self, url):
        response = self.send_get(url)
        # Returns 3rd parentheses group
        csrf_token = re.search('<input(.*)id="csrf_token"(.*)value="(.+)"(/?)>', response.data).group(3)
        return csrf_token

    def get_faculty_bio_id(self, responseData):
        return re.search('id="faculty_bio_id".*value="(.+)"', responseData).group(1)

    def create_form_submission(self, f_b_id, job_title):
        return {
            'csrf_token': self.csrf_token,
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
        response = self.send_get("/faculty-bio/new")
        self.csrf_token = self.get_csrf_token("/faculty-bio/new")
        assert b'<form id="facultybioform" action="/faculty-bio/submit" method="post" enctype="multipart/form-data">' \
               in response.data

        # Send the form submission to create it in Cascade
        form_contents = self.create_form_submission("", "Web Developer")
        response = self.send_post("/faculty-bio/submit", form_contents)
        self.faculty_bio_id = self.get_faculty_bio_id(response.data)
        assert b"<p>You've successfully created a new bio. Your brand new bio has been sent for approval but will be " \
               b"ready to view in 2-3 business days.</p>" in response.data

        # O`pen up the new bio to edit it
        response = self.send_get("/faculty-bio/edit/" + self.faculty_bio_id)
        assert b'<form id="facultybioform" action="/faculty-bio/submit" method="post" enctype="multipart/form-data">' \
               in response.data

        # Send the edited form to update the bio
        form_contents = self.create_form_submission(self.faculty_bio_id, "Web Developers")
        response = self.send_post("/faculty-bio/submit", form_contents)
        assert b"You've successfully edited your bio. Your edits have been sent for approval but will be ready to " \
               b"view in 2-3 business days. Thanks for keeping your bio up to date!" in response.data

        # Delete the new bio to make sure these tests don't bloat Cascade
        time.sleep(20)
        response = self.send_get("/faculty-bio/delete/" + self.faculty_bio_id)
        assert b'Your faculty bio has been deleted. It will be removed from your' in response.data

    def tearDown(self):
        pass
