import re

from testing_suite.integration_tests import IntegrationTestCase


class EAnnouncementsInvalidUnicodeSubmission(IntegrationTestCase):

    def __init__(self, methodName):
        super(EAnnouncementsInvalidUnicodeSubmission, self).__init__(methodName)
        self.eaid = None
        self.request_type = "POST"
        self.request = self.generate_url("submit")

    def get_eaid(self, text):
        return re.search('<input(.*)id="new_eaid"(.*)value="(.+)"(/?)>', text).group(3)

    def create_form(self):
        # &rsquo; => ' is the problem
        to_return = {
            'title': "Podcasting iStudio Monday December 4, 4-5pm",
            'message': "<p>Join us for the next Innovation Studio in the Makerspace (University Library - HC302) "
                       "on Monday, December 4 from 4:00-5:00pm. Sam Mulberry (History) and Chris Moore (Political "
                       "Science) will show how they create podcasts, like <em>Election Shock Therapy</em>, by "
                       "making one with your help. Come prepared to discuss and learn the hows and whys of podcasting "
                       "including how to use it in your teaching. If you&rsquo;re a little curious or are already "
                       "interested in doing one, meet us in the Makerspace to take that next step.</p>\r\n\r\n<p>CAS "
                       "Faculty Development</p>\r\n",
            'first_date': "12-01-2017",
            'second_date': "12-04-2017",
            'banner_roles': "FACULTY-CAS"
        }
        return to_return

    def test_submit_invalid_unicode(self):
        # Because the ID returned will always be different, we can't assertEqual; have to use the old assertIn
        expected_response = b"You've successfully created your E-Announcement. Once your E-Announcement has been approved,"
        form = self.create_form()
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)
        self.eaid = self.get_eaid(response.data)
        print "eaid:", self.eaid
