import re
import tinker
import unittest


class EventsBaseTestCase(unittest.TestCase):

    def setUp(self):
        tinker.app.testing = True
        self.app = tinker.app.test_client()
        self.csrf_token = None
        self.eid = None

    def send_post(self, url, form_contents):
        return self.app.post(url, data=form_contents, follow_redirects=True)

    def send_get(self, url):
        return self.app.get(url, follow_redirects=True)

    def get_csrf_token(self, url):
        response = self.send_get(url)
        # Returns 3rd parentheses group
        csrf_token = re.search('<input(.*)id="csrf_token"(.*)value="(.+)"(/?)>', response.data).group(3)
        return csrf_token

    def get_eid(self, responseData):
        return re.search('<input type="hidden" id="new_eid" value="(.+)"(/?)>', responseData).group(1)

    def create_form(self, title):
        to_return = {
            'csrf_token': self.csrf_token,
            'title': title,  # Event name
            'metaDescription': "This is an event created via unit testing",  # Teaser
            'featuring': "Testing things!",  # Featuring
            'sponsors': "Eric Jameson",  # Sponsors
            'main_content': "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",  # Event description
            'start1': "August 3rd 2016, 12:00 am",
            'end1': "August 5th 2016, 12:00 am",
            'location': "On Campus",  # Location
            'on_campus_location': "Clauson Center (CC)",  # On campus location
            'other_on_campus': "No.",  # Other on campus location
            'maps_directions': "Don't drive; take a plane.",  # Instructions for Guests
            'registration_heading': "Registration",  # Select a heading for the registration section
            'registration_details': "Pay all the money.",  # Registration/ticketing details
            'wufoo_code': "",
            'cost': "$20",  # Cost
            'cancellations': "Full refund",  # Cancellations and refunds
            'questions': "Why are you still reading this event? It's just a test!",  # Questions
            'general': "Athletics",  # General categories
            'offices': "Parents",  # Offices
            'cas_departments': "English",  # CAS academic department
            'adult_undergrad_program': "None",  # CAPS programs
            'seminary_program': "None",  # Seminary programs
            'graduate_program': "None",  # GS Programs
            'internal': "None",  # Internal only
            'image': "",
            'off_campus_location': "",
            'ticketing_url': "",
            'timezone1': "",
            'link': "",
            'num_dates': "1",
            'author': "",
        }
        if self.eid:
            to_return['event_id'] = self.eid
        else:
            to_return['event_id'] = ""
        return to_return

    def test_sequence(self):
        # Get new form
        response = self.send_get("event/add")
        self.csrf_token = self.get_csrf_token("event/add")
        assert b'<p>If you have any questions as you submit your event, please contact Conference and Event Services at 651.638.6090.</p>' in response.data

        # Submit new form
        response = self.send_post("event/submit", self.create_form("Test event"))
        self.eid = self.get_eid(response.data)
        assert b"<p>You'll receive an email when your event has been approved by Conference and Event Services. Once your event has been approved, it will appear on your Tinker" in response.data

        # Get edit form of new object
        response = self.send_get("event/edit/" + self.eid)
        assert b'<p>If you have any questions as you submit your event, please contact Conference and Event Services at 651.638.6090.</p>' in response.data

        # Submit edited form
        response = self.send_post("event/submit", self.create_form("Edited title"))
        assert b"<p>You'll receive an email when your event has been approved by Conference and Event Services. Once your event has been approved, it will appear on your Tinker" in response.data

        # Duplicate edited object
        response = self.send_get("event/duplicate/" + self.eid)
        assert b'<p>If you have any questions as you submit your event, please contact Conference and Event Services at 651.638.6090.</p>' in response.data

        # Delete the testing object
        response = self.send_get("event/delete/" + self.eid)
        assert b'Your event has been deleted. It will be removed from your' in response.data

    def tearDown(self):
        pass

if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
