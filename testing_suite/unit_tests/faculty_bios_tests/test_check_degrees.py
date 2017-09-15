from faculty_bios_controller_base import FacultyBiosControllerBaseTestCase


class CheckDegreesTestCase(FacultyBiosControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CheckDegreesTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_check_degrees_valid(self):
        test_form = {
            'website': u'None.',
            'image': u'',
            'degree-earned1': u'B.S. of Computer Science',
            'graduate1': u'None',
            'teaching_specialty': u'<p>asdf11</p>\r\n',
            'seminary1': u'None',
            'hobbies': u'<p>asdf8</p>\r\n',
            'school1': u'Bethel University',
            'research_interests': u'<p>asdf10</p>\r\n',
            'biography': u'<p>asdf1</p>\r\n',
            'program-director1': u'No',
            'faculty_bio_id': u'',
            'undergrad1': u'Math & Computer Science',
            'certificates': u'<p>asdf6</p>\r\n',
            'email': u'phg49389@bethel.edu',
            'first': u'Philip',
            'new-job-title1': u'Web Developer',
            'started_at_bethel': u'2011',
            'quote': u'Arbitrarily compulsive, compulsively arbitrary.',
            'year1': u'2016',
            'awards': u'<p>asdf3</p>\r\n',
            'last': u'Gibbens',
            'adult-undergrad1': u'None',
            'areas': u'<p>asdf9</p>\r\n',
            'organizations': u'<p>asdf7</p>\r\n',
            'schools1': u'College of Arts and Sciences',
            'num_degrees': u'1',
            'author_faculty': u'phg49389',
            'dept-chair1': u'No',
            'presentations': u'<p>asdf5</p>\r\n',
            'courses': u'<p>asdf2</p>\r\n',
            'image_url': u'',
            'publications': u'<p>asdf4</p>\r\n',
            'highlight': u"A great magazine for the dentist's office",
            'num_new_jobs': u'1',
            'num_jobs': u'0',
            'faculty_location': u'St. Paul',
            'lead-faculty1': u'Other'
        }
        response = self.controller.check_degrees(test_form)
        self.assertTrue(isinstance(response, tuple))
        self.assertEqual(len(response), 4)
        self.assertTrue(isinstance(response[0], str))
        self.assertEqual(response[0], '{"school1": "Bethel University", "year1": "2016", "degree-earned1": '
                                      '"B.S. of Computer Science"}')
        self.assertTrue(isinstance(response[1], bool))
        self.assertTrue(response[1])
        self.assertTrue(isinstance(response[2], list))
        self.assertEqual(len(response[2]), 0)
        self.assertTrue(isinstance(response[3], int))
        self.assertEqual(response[3], 1)
