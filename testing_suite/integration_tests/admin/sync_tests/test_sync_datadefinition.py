import json

from testing_suite.integration_tests import BaseIntegrationTestCase


class DataDefinitionTestCase(BaseIntegrationTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(DataDefinitionTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("datadefinition")

    def create_form(self, asset_id="yes"):
        return json.dumps({
            'id': asset_id
        })

    #######################
    ### Testing methods ###
    #######################

    def test_datadefinition_valid(self):
        expected_response = repr('\x14#\x0c\xfc\x81\xbd\xf2=\n\xd78D\xd7n\xc7\x92')  # b'<h3>Successfully Synced'
        form = self.create_form()
        response = self.send_post(self.request, form)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)

    def test_datadefinition_invalid_id(self):
        expected_response = self.ERROR_400
        arg_names = ['asset_id']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: None}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            short_string = self.get_unique_short_string(response.data)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/datadefinition_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertEqual(expected_response, short_string, msg=failure_message)