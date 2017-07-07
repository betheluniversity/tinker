from testing_suite.integration_tests import BaseIntegrationTestCase


class SubmitTestCase(BaseIntegrationTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SubmitTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("submit")

    def create_form(self, url="/yes"):
        return {
            'url': url
        }

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        expected_response = repr('\xcd\xca\xa2jc\xc5NC\xf2\xa5`(_\xc0\x9d\xb1')
        # Right now this test finishes just fine, but the method it tests is throwing an error. In tinker/tools.py, the
        # method clear_image_cache(image_path) is calling the commandline command "rm" on folders that aren't there.
        # As far as I can tell, this is because the method is written to work on the production server and references
        # files and folders in there, not on my local machine.
        form_contents = self.create_form()
        response = self.send_post(self.request, form_contents)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)

    def test_submit_invalid(self):
        expected_response = self.ERROR_400
        arg_names = ['url']
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
