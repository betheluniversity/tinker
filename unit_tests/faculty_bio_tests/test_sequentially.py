import re
import time
import tinker
import unittest

# TODO: look for ways to have csrf token and faculty bio be stored globally across the test suite somehow

class SequentialTestCase(unittest.TestCase):

    def setUp(self):
        self.app = tinker.app.test_client()
        self.csrf_token = None
        self.faculty_bio_id = None

    def send_post(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True)

    def send_get(self, url):
        return self.app.get(url, follow_redirects=True)

    def create_form_submission(self, csrf, f_b_id, job_title):
        return {
            'csrf_token': u'' + csrf,
            'faculty_bio_id': u'' + f_b_id,
            'image_url': u'',
            'first': u'Philip',
            'last': u'Gibbens',
            'author': u'phg49389',
            'num_jobs': u'0',
            'num_new_jobs': u'1',
            'schools1': u'Bethel University',
            'graduate1': u'None',
            'seminary1': u'None',
            'undergrad1': u'None',
            'adult-undergrad1': u'None',
            'new-job-title1': u'' + job_title,
            'email': u'phg49389@bethel.edu',
            'started_at_bethel': u'2011',
            'heading': u'Areas of expertise',
            'teaching_specialty': u'',
            'research_interests': u'',
            'areas': u'asdf',
            'num_degrees': u'1',
            'school1': u'Bethel University',
            'degree-earned1': u'B.S. of Computer Science',
            'year1': u'2016',
            'biography': u'<p>asdf</p>\r\n',
            'courses': u'<p>asdf</p>\r\n',
            'awards': u'<p>adsf</p>\r\n',
            'publications': u'<p>asdf</p>\r\n',
            'presentations': u'<p>asdf</p>\r\n',
            'certificates': u'<p>asdf</p>\r\n',
            'organizations': u'<p>asdf</p>\r\n',
            'hobbies': u'<p>asdf</p>\r\n',
            'quote': u'Arbitrarily compulsive, compulsively arbitrary.',
            'website': u'None.',
        }

    def test_all_of_them(self):
        # Get a new form to fill out
        response = self.send_get("/faculty-bio/new")
        m = re.search('id="csrf_token".*value=".*"', response.data)
        self.csrf_token = m.group(0).split('value="')[1][:-1]
        assert b'<form id="facultybioform" action="/faculty-bio/submit" method="post" enctype="multipart/form-data">' \
               in response.data

        # Send the form submission to create it in Cascade
        form_contents = self.create_form_submission(self.csrf_token, "", "Web Developer")
        response = self.send_post("/faculty-bio/submit", form_contents)
        m = re.search('id="faculty_bio_id".*value=".*"', response.data)
        self.faculty_bio_id = m.group(0).split('value="')[1][:-1]
        assert b"<p>You've successfully created a new bio. Your brand new bio has been sent for approval but will be " \
               b"ready to view in 2-3 business days.</p>" in response.data

        # O`pen up the new bio to edit it
        response = self.send_get("/faculty-bio/edit/" + self.faculty_bio_id)
        assert b'<form id="facultybioform" action="/faculty-bio/submit" method="post" enctype="multipart/form-data">' \
               in response.data

        # Send the edited form to update the bio
        form_contents = self.create_form_submission(self.csrf_token, self.faculty_bio_id, "Web Developers")
        response = self.send_post("/faculty-bio/submit", form_contents)
        assert b"You've successfully edited your bio. Your edits have been sent for approval but will be ready to " \
               b"view in 2-3 business days. Thanks for keeping your bio up to date!" in response.data

        # Delete the new bio to make sure these tests don't bloat Cascade
        time.sleep(20)
        response = self.send_get("/faculty-bio/delete/" + self.faculty_bio_id)
        assert b'Your faculty bio has been deleted. It will be removed from your <a href="https://tinker.bethel.edu">' \
               b'Tinker homepage</a> in a few minutes.' in response.data

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
