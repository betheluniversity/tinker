import json

from program_search_base import ProgramSearchBaseTestCase


class SubmitTestCase(ProgramSearchBaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SubmitTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("submit")

    def create_form(self, key="x", tag="z", outcome="False", topic="False", other="False"):
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
        expected_response = repr('%Ty\x9eO\xa4\xf3/\x87\xa3\xe0Vh3\x17V')
        # b'<label for="key" style="color: #252422">Concentration Code or Program Name:</label>'
        form_contents = self.create_form()
        response = self.send_post(self.request, form_contents)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)

    def test_submit_invalid_successes(self):
        expected_response = repr('%Ty\x9eO\xa4\xf3/\x87\xa3\xe0Vh3\x17V')
        # b'<label for="key" style="color: #252422">Concentration Code or Program Name:</label>'
        arg_names = ['key', 'tag']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: None}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            short_string = self.get_unique_short_string(response.data)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/submit_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertEqual(expected_response, short_string, msg=failure_message)

    def test_submit_invalid_failures(self):
        expected_response = self.ERROR_400
        arg_names = ['outcome', 'topic', 'other']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: None}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            short_string = self.get_unique_short_string(response.data)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/submit_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertEqual(expected_response, short_string, msg=failure_message)

