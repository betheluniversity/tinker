from program_search_base import ProgramSearchBaseTestCase
import json
import xml.dom.minidom as XML


class SubmitTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SubmitTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("submit")

    def create_form(self, key, tag, outcome, topic, other):
        return json.dumps({
            'key': key,
            'tag': tag,
            'outcome': outcome,
            'topic': topic,
            'other': other
        })

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        expected_response = b'<label for="key" style="color: #252422">Concentration Code or Program Name:</label>'
        form_contents = self.create_form("x", "z", "False", "False", "False")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_submit_invalid_key(self):
        expected_response = b'<label for="key" style="color: #252422">Concentration Code or Program Name:</label>'
        form_contents = self.create_form(None, "z", "False", "False", "False")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_submit_invalid_tag(self):
        expected_response = b'<label for="key" style="color: #252422">Concentration Code or Program Name:</label>'
        form_contents = self.create_form("x", None, "False", "False", "False")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_submit_invalid_outcome(self):
        expected_response = self.ERROR_500
        form_contents = self.create_form("x", "z", None, "False", "False")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_submit_invalid_topic(self):
        expected_response = self.ERROR_500
        form_contents = self.create_form("x", "z", "False", None, "False")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_submit_invalid_other(self):
        expected_response = self.ERROR_500
        form_contents = self.create_form("x", "z", "False", "False", None)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
