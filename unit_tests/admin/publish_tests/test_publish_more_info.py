from unit_tests import BaseTestCase


class MoreInfoTestCase(BaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(MoreInfoTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("more_info")

    def create_form(self, asset_type="page", asset_id="a7404faa8c58651375fc4ed23d7468d5"):
        return {
            'type': asset_type,
            'id': asset_id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_more_info_valid(self):
        # This test keeps changing its response, so it will fail with an assertEqual on shortstrings
        # As such, I'm leaving it the old style of assertIn
        expected_response = b'<div class="col-sm-6 zero-left-padding">'
        form = self.create_form("page", "a7404faa8c58651375fc4ed23d7468d5")
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_more_info_invalid(self):
        expected_response = self.ERROR_400
        arg_names = ['asset_type', 'asset_id']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: None}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            short_string = self.get_unique_short_string(response.data)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/more_info_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertEqual(expected_response, short_string, msg=failure_message)
