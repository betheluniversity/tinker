import json

from unit_tests import BaseTestCase


class MetadataTestCase(BaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(MetadataTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("metadata")

    def create_form(self, sync_id="yes"):
        return json.dumps({
            'id': sync_id
        })

    #######################
    ### Testing methods ###
    #######################

    def test_metadata_valid(self):
        expected_response = b'<h3>Successfully Synced'
        form = self.create_form("yes")
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_metadata_invalid(self):
        expected_response = self.ERROR_400
        arg_names = ['sync_id']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: None}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/metadata_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertIn(expected_response, response.data, msg=failure_message)