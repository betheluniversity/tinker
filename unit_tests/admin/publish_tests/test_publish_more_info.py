from unit_tests import BaseTestCase


class MoreInfoTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(MoreInfoTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("more_info")

    def create_form(self, type, id):
        return {
            'type': type,
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_more_info_valid(self):
        expected_response = b'<div class="col-sm-6 zero-left-padding">'
        form_contents = self.create_form("page", "a7404faa8c58651375fc4ed23d7468d5")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_more_info_invalid_type(self):
        expected_response = self.ERROR_400
        form_contents = self.create_form(None, "a7404faa8c58651375fc4ed23d7468d5")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_more_info_invalid_id(self):
        expected_response = self.ERROR_400
        form_contents = self.create_form("page", None)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)