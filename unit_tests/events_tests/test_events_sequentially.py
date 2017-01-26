import re
from unit_tests import BaseTestCase


class EventsSequentialTestCase(BaseTestCase):

    def __init__(self, methodName):
        super(EventsSequentialTestCase, self).__init__(methodName)
        self.eid = None
        self.request_type = ""
        self.request = ""

    def get_eid(self, responseData):
        return re.search('<input type="hidden" id="new_eid" value="(.+)"(/?)>', responseData).group(1)

    def create_form(self, title, meta_description, featuring, sponsors, main_content, start, end, location,
                    on_campus_location, other_on_campus, maps_directions, registration_heading, registration_details,
                    wufoo_code, cost, cancellations, questions, general, offices, cas_departments,
                    adult_undergrad_program, seminary_program, graduate_program, internal, image, off_campus_location,
                    ticketing_url, timezone, link, author, eid=None):
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
        form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
                                "Eric Jameson",
                                "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
                                "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
                                "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
                                "Pay all the money.", "", "$20", "Full refund",
                                "Why are you still reading this event? It's just a test!",
                                "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
                                "")
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)
        self.eid = self.get_eid(response.data)

    def submit_new_form_all_invalid_types(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b'There were errors with your form'
        arg_names = ["title", "meta_description", "featuring", "sponsors", "main_content", "start", "end", "location",
                     "on_campus_location", "other_on_campus", "maps_directions", "registration_heading",
                     "registration_details", "wufoo_code", "cost", "cancellations", "questions", "general", "offices",
                     "cas_departments", "adult_undergrad_program", "seminary_program", "graduate_program", "internal",
                     "image", "off_campus_location", "ticketing_url", "timezone", "link", "author"]
        valid_form_array = ["Test event", "This is an event created via unit testing", "Testing things!", "Eric Jameson",
                      "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
                      "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus", "Clauson Center (CC)",
                      "No.", "Don't drive; take a plane.", "Registration", "Pay all the money.", "", "$20",
                      "Full refund", "Why are you still reading this event? It's just a test!", "Athletics", "Parents",
                      "English", "None", "None", "None", "None", "", "", "", "", "", ""]
        for index in range(30):
            invalid_form_array = valid_form_array
            invalid_form_array[index] = ""
            form = self.create_form(*invalid_form_array)
            response = self.send_post(self.request, form)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/new_invalid_" + arg_names[index],
                                                            self.get_line_number())
            self.assertIn(expected_response, response.data, msg=failure_message)

    # def submit_new_form_invalid_meta_description(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = b'There were errors with your form'
    #     form = self.create_form("Test event", None, "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_featuring(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = b'There were errors with your form'
    #     form = self.create_form("Test event", "This is an event created via unit testing", "",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     # response = self.send_post(self.request, form)
    #     # failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #     #                                                 expected_response, self.class_name, self.get_line_number())
    #     # self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_sponsors(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = b'There were errors with your form'
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     # response = self.send_post(self.request, form)
    #     # failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #     #                                                 expected_response, self.class_name, self.get_line_number())
    #     # self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_main_content(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = b'There were errors with your form'
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     # response = self.send_post(self.request, form)
    #     # failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #     #                                                 expected_response, self.class_name, self.get_line_number())
    #     # self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_start(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = b'There were errors with your form'
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_end(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = b'There were errors with your form'
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_location(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = b'There were errors with your form'
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     # response = self.send_post(self.request, form)
    #     # failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #     #                                                 expected_response, self.class_name, self.get_line_number())
    #     # self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_on_campus_location(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = b'There were errors with your form'
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_other_on_campus(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", None, "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_maps_directions(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", None, "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_registration_heading(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", None,
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_registration_details(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             None, "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_wufoo_code(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", None, "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_cost(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", None, "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_cancellations(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", None,
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_questions(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             None,
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_general(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             None, "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_offices(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", None, "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_cas_departments(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", None, "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_adult_undergrad_program(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", None, "None", "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_seminary_program(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", None, "None", "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_graduate_program(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", None, "None", "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_internal(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", None, "", "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_image(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", None, "", "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_off_campus_location(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", None, "", "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_ticketing_url(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", None, "", "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_timezone(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", None, "",
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_link(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", None,
    #                             "1", "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_num_dates(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             None, "")
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_new_form_invalid_author(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Test event", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", None)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)

    def get_edit_form(self):
        self.request_type = "GET"
        self.request = self.generate_url("edit", event_id=self.eid)
        expected_response = b'<p>If you have any questions as you submit your event, please contact Conference and Event Services'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertNotIn(expected_response, response.data, msg=failure_message)

    def submit_edit_valid(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b'Take a short break in your day and enjoy this GIF!'
        form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
                                "Eric Jameson",
                                "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
                                "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
                                "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
                                "Pay all the money.", "", "$20", "Full refund",
                                "Why are you still reading this event? It's just a test!",
                                "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
                                "", eid=self.eid)
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def submit_edit_all_invalid_types(self):
        self.request_type = "POST"
        self.request = self.generate_url("submit")
        expected_response = b'There were errors with your form'
        arg_names = ["title", "meta_description", "featuring", "sponsors", "main_content", "start", "end", "location",
                     "on_campus_location", "other_on_campus", "maps_directions", "registration_heading",
                     "registration_details", "wufoo_code", "cost", "cancellations", "questions", "general", "offices",
                     "cas_departments", "adult_undergrad_program", "seminary_program", "graduate_program", "internal",
                     "image", "off_campus_location", "ticketing_url", "timezone", "link", "author"]
        valid_form_array = ["Edited title", "This is an event created via unit testing", "Testing things!",
                            "Eric Jameson",
                            "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
                            "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
                            "Clauson Center (CC)",
                            "No.", "Don't drive; take a plane.", "Registration", "Pay all the money.", "", "$20",
                            "Full refund", "Why are you still reading this event? It's just a test!", "Athletics",
                            "Parents",
                            "English", "None", "None", "None", "None", "", "", "", "", "", ""]
        for index in range(30):
            invalid_form_array = valid_form_array
            invalid_form_array[index] = ""
            form = self.create_form(*invalid_form_array, eid=self.eid)
            response = self.send_post(self.request, form)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/edit_invalid_" + arg_names[index],
                                                            self.get_line_number())
            self.assertIn(expected_response, response.data, msg=failure_message)

    # def submit_edit_invalid_meta_description(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", None, "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_featuring(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", None,
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_sponsors(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             None,
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_main_content(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             None,
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_start(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             None, "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_end(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", None, "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_location(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", None,
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_on_campus_location(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             None, "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_other_on_campus(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", None, "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_maps_directions(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", None, "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_registration_heading(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", None,
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_registration_details(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             None, "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_wufoo_code(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", None, "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_cost(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", None, "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_cancellations(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", None,
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_questions(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             None,
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_general(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             None, "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_offices(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", None, "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_cas_departments(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", None, "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_adult_undergrad_program(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", None, "None", "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_seminary_program(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", None, "None", "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_graduate_program(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", None, "None", "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_internal(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", None, "", "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_image(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", None, "", "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_off_campus_location(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", None, "", "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_ticketing_url(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", None, "", "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_timezone(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", None, "",
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_link(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", None,
    #                             "1", "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_num_dates(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             None, "", eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)
    #
    # def submit_edit_invalid_author(self):
    #     self.request_type = "POST"
    #     self.request = self.generate_url("submit")
    #     expected_response = self.ERROR_400
    #     form = self.create_form("Edited title", "This is an event created via unit testing", "Testing things!",
    #                             "Eric Jameson",
    #                             "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
    #                             "August 3rd 2017, 12:00 am", "August 5th 2017, 12:00 am", "On Campus",
    #                             "Clauson Center (CC)", "No.", "Don't drive; take a plane.", "Registration",
    #                             "Pay all the money.", "", "$20", "Full refund",
    #                             "Why are you still reading this event? It's just a test!",
    #                             "Athletics", "Parents", "English", "None", "None", "None", "None", "", "", "", "", "",
    #                             "1", None, eid=self.eid)
    #     response = self.send_post(self.request, form)
    #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
    #                                                     expected_response, self.class_name, self.get_line_number())
    #     self.assertIn(expected_response, response.data, msg=failure_message)

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
        expected_response = b'Your event has been deleted. It will be removed from your'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_sequence(self):
        # To be clear, these events do get made in Cascade, and they are publicly visible. If they're not deleted, they
        # will be located in /events/2017/athletics/. Also, when created, they will go to workflow, so the /edit
        # endpoint doesn't work.

        self.get_new_form()

        self.submit_new_form_valid()
        self.submit_new_form_all_invalid_types()

        self.get_edit_form()

        self.submit_edit_valid()
        self.submit_edit_all_invalid_types()

        self.get_duplicate_form()

        self.delete_testing_object()
