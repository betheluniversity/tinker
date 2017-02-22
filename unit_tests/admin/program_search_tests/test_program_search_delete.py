import json

from program_search_base import ProgramSearchBaseTestCase


class MultiDeleteTestCase(ProgramSearchBaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(MultiDeleteTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("multi_delete")

    def create_form(self, cache_id="2044"):
        return json.dumps([cache_id])

    #######################
    ### Testing methods ###
    #######################

    def test_multi_delete(self):
        expected_response = b'Deleted ids:'
        form = self.create_form()
        response = self.send_post(self.request, form)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_multi_delete_invalid(self):
        expected_response = "One of the ids given to this method was not a string"
        arg_names = ['cache_id']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: None}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/multi_delete_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertIn(expected_response, response.data, msg=failure_message)