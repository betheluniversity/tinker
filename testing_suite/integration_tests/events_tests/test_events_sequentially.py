import re

from testing_suite.integration_tests import IntegrationTestCase


class EventsSequentialTestCase(IntegrationTestCase):

    def __init__(self, methodName):
        super(EventsSequentialTestCase, self).__init__(methodName)
        self.eid = None
        self.request_type = ""
        self.request = ""

    def get_eid(self, responseData):
        return re.search('<input type="hidden" id="new_eid" value="(.+)"(/?)>', responseData).group(1)

    def create_form(self, title='Integration Test -- Delete if submitted', meta_description="This event should not be approved or published; it's supposed to be deleted automatically",
                    featuring='Web Developers', sponsors='<p>Nike</p>\r\n', main_content='<p>Units will be tested, and then integrated. Or should I say: "anti-derived"</p>\r\n',
                    start='October 11th 2019, 9:00 am', end='October 11th 2019, 6:00 pm', location="On Campus",
                    on_campus_location='Anderson Center Community Room', other_on_campus='',
                    maps_directions='<p>Forget that we ever met</p>\r\n', registration_heading="Registration",
                    registration_details='<p>Register for learning</p>\r\n', wufoo_code="", cost='Knowledge is priceless',
                    cancellations="You can't unlearn things.", questions='<p>If you see this event, please contact the ITS Help Desk.</p>\r\n',
                    general='None', offices='None', cas_departments='None', adult_undergrad_program='None',
                    seminary_program='None', graduate_program='None', internal='None', image="", off_campus_location="",
                    ticketing_url="", timezone="", link='https://www.google.com', author="", eid=None):
        to_return = {
            'title': title,  # Event name
            'metaDescription': meta_description,  # Teaser
            'featuring': featuring,  # Featuring
            'sponsors': sponsors,  # Sponsors
            'main_content': main_content,  # Event description
            'start1': start,
            'end1': end,
            'location': location,  # Location
            'on_campus_location': on_campus_location,  # On campus location
            'other_on_campus': other_on_campus,  # Other on campus location
            'maps_directions': maps_directions,  # Instructions for Guests
            'registration_heading': registration_heading,  # Select a heading for the registration section
            'registration_details': registration_details,  # Registration/ticketing details
            'wufoo_code': wufoo_code,
            'cost': cost,  # Cost
            'cancellations': cancellations,  # Cancellations and refunds
            'questions': questions,  # Questions
            'general': general,  # General categories
            'offices': offices,  # Offices
            'cas_departments': cas_departments,  # CAS academic department
            'adult_undergrad_program': adult_undergrad_program,  # CAPS programs
            'seminary_program': seminary_program,  # Seminary programs
            'graduate_program': graduate_program,  # GS Programs
            'internal': internal,  # Internal only
            'image': image,
            'off_campus_location': off_campus_location,
            'ticketing_url': ticketing_url,
            'timezone1': timezone,
            'link': link,
            'num_dates': "1",
            'author': author,
        }
        if eid:
            to_return['event_id'] = eid
        else:
            to_return['event_id'] = ""
        return to_return

    def get_new_form(self):
        self.request_type = "GET"
        self.request = self.generate_url("add")
        expected_response = b'<p>If you have any questions as you submit your event, please contact Conference and Event Services'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_new_form_valid(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b'Take a short break in your day and enjoy this GIF!'
        form = self.create_form()
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)
        self.eid = self.get_eid(response.data)

    def submit_new_form_invalid(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b'There were errors with your form'
        arg_names = ['title', 'meta_description', 'general', 'offices', 'cas_departments', 'adult_undergrad_program',
                     'seminary_program', 'graduate_program', 'internal']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: ""}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/new_form_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertIn(expected_response, response.data, msg=failure_message)

    def get_edit_form(self):
        self.request_type = "GET"
        self.request = self.generate_url("edit", event_id=self.eid)
        expected_response = b'<p>If you have any questions as you submit your event, please contact Conference and Event Services'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_valid(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b'Take a short break in your day and enjoy this GIF!'
        form = self.create_form(title="Edited title", eid=self.eid)
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def get_duplicate_form(self):
        self.request_type = "GET"
        self.request = self.generate_url("duplicate", event_id=self.eid)
        expected_response = b'<p>If you have any questions as you submit your event, please contact Conference and Event Services'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def delete_testing_object(self):
        self.request = self.generate_url("delete", event_id=self.eid)
        expected_response = repr('2\xc7$\xf0\x96?ii\xec*\t\xa0B\xfc8"')
        # b'Your event has been deleted. It will be removed from your'
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)

    def test_sequence(self):
        # To be clear, these events do get made in Cascade, and they are publicly visible. If they're not deleted, they
        # will be located in /events/2017/athletics/. Also, when created, they will go to workflow, so the /edit
        # endpoint doesn't work.

        self.get_new_form()

        self.submit_new_form_valid()
        self.submit_new_form_invalid()

        self.get_edit_form()

        self.submit_edit_valid()

        self.get_duplicate_form()

        self.delete_testing_object()
