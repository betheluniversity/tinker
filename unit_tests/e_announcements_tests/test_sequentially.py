import re
import tinker
import unittest


class EAnnouncementsBaseTestCase(unittest.TestCase):

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        tinker.app.testing = True
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        self.app = tinker.app.test_client()

    def send_post(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True)

    def send_get(self, url):
        return self.app.get(url, follow_redirects=True)

    def get_eaid(self, text):
        return re.search('<input(.*)id="new_eaid"(.*)value="(.+)"(/?)>', text).group(3)

    def create_form(self, title, eaid=None):
        to_return = {
            'title': title,
            'message': "This E-Announcement should never be seen by the public, I hope",
            'name': "Philip Gibbens",
            'email': "phg49389@bethel.edu",
            'first_date': '08-01-2017',
            'second_date': '08-05-2017',
            'banner_roles': 'STUDENT-CAS'
        }
        if eaid:
            to_return['e_announcement_id'] = eaid
        return to_return

    def test_sequence(self):
        # Get new form
        response = self.send_get("/e-announcement/new")
        assert b'<form id="eannouncementform" action="/e-announcement/submit" method="post" enctype="multipart/form-data">' in response.data

        # Submit the new form to create a new object
        response = self.send_post("/e-announcement/submit", self.create_form("First title"))
        assert b"You've successfully created your E-Announcement. Once your E-Announcement has been approved, it will appear on your Tinker" in response.data
        self.eaid = self.get_eaid(response.data)

        ###################################################################################
        ### The new submission goes to workflow; thus /edit and /duplicate should fail. ###
        ###################################################################################

        # Get edit form
        response = self.send_get("/e-announcement/edit/" + self.eaid)
        assert b'<input type="hidden" name="e_announcement_id" id="e_announcement_id" value="' not in response.data

        # Edit that new object
        response = self.send_post("/e-announcement/submit", self.create_form("Second title", eaid=self.eaid))
        assert b"You've successfully edited your E-Announcement. Once your E-Announcement has been approved, it will appear on your Tinker" in response.data

        # Call the duplicate form to make sure it works
        response = self.send_get("/e-announcement/duplicate/" + self.eaid)
        assert b'<form id="eannouncementform" action="/e-announcement/submit" method="post" enctype="multipart/form-data">' not in response.data

        # Delete the new object
        response = self.send_get("/e-announcement/delete/" + self.eaid)
        assert b'Your E-Announcements has been deleted. It will be removed from your' in response.data

    # Corresponding to the setUp method, this method deletes the temporary database
    def tearDown(self):
        pass

if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)