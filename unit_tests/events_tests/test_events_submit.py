from unit_tests import BaseTestCase


class SubmitTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SubmitTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "POST"
        self.request = self.generate_url("submit")

    def create_form(self, end1, other_on_campus, on_campus_location, author, wufoo_code, main_content, image, timezone1, cas_departments, sponsors, off_campus_location, general, adult_undergrad_program, cost, link, questions, registration_heading, num_dates, registration_details, featuring, title, event_id, metaDescription, start1, cancellations, maps_directions, internal, offices, location, graduate_program, ticketing_url, seminary_program):
        return {
            'end1': end1,
            'other_on_campus': other_on_campus,
            'on_campus_location': on_campus_location,
            'author': author,
            'wufoo_code': wufoo_code,
            'main_content': main_content,
            'image': image,
            'timezone1': timezone1,
            'cas_departments': cas_departments,
            'sponsors': sponsors,
            'off_campus_location': off_campus_location,
            'general': general,
            'adult_undergrad_program': adult_undergrad_program,
            'cost': cost,
            'link': link,
            'questions': questions,
            'registration_heading': registration_heading,
            'num_dates': num_dates,
            'registration_details': registration_details,
            'featuring': featuring,
            'title': title,
            'event_id': event_id,
            'metaDescription': metaDescription,
            'start1': start1,
            'cancellations': cancellations,
            'maps_directions': maps_directions,
            'internal': internal,
            'offices': offices,
            'location': location,
            'graduate_program': graduate_program,
            'ticketing_url': ticketing_url,
            'seminary_program': seminary_program
        }

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        expected_response = b'You'll receive an email when your event has been approved by Conference and Event Services. Once your'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_end1(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form(None, "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_other_on_campus(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", None, "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_on_campus_location(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", None, "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_author(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", None, "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_wufoo_code(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", None, "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_main_content(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", None, "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_image(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", None, "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_timezone1(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", None, "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_cas_departments(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", None, "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_sponsors(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", None, "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_off_campus_location(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", None, "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_general(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", None, "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_adult_undergrad_program(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", None, "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_cost(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", None, "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_link(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", None, "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_questions(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", None, "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_registration_heading(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", None, "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_num_dates(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", None, "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_registration_details(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", None, "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_featuring(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", None, "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_title(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", None, "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_event_id(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", None, "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_metaDescription(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", None, "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_start1(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", None, "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_cancellations(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", None, "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_maps_directions(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", None, "None", "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_internal(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", None, "Parents", "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_offices(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", None, "On Campus", "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_location(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", None, "None", "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_graduate_program(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", None, "", "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_ticketing_url(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", None, "None")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_seminary_program(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("August 5th 2017, 12:00 am", "No.", "Clauson Center (CC)", "", "", "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes", "", "", "English", "Eric Jameson", "", "Athletics", "None", "$20", "", "Why are you still reading this event? It's just a test!", "Registration", "1", "Pay all the money.", "Testing things!", "Test event", "", "This is an event created via unit testing", "August 3rd 2017, 12:00 am", "Full refund", "Don't drive; take a plane.", "None", "Parents", "On Campus", "None", "", None)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
