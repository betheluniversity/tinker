from faculty_bio_base import FacultyBioBaseTestCase


class SubmitTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form_submission(self):
        return {
            'csrf_token': u'1467131403##9e1f97565c5aac366d4d1cf16eee8a8c91931032',
            'faculty_bio_id': u'',
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
            'new-job-title1': u'Web Developer',
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

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        form_contents = self.create_form_submission()
        response = self.send_post("/faculty-bio/submit", form_contents)
        print response.data
        assert b'???????' in response.data
