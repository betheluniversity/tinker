from program_search_base import ProgramSearchBaseTestCase
import json


class MultiDeleteTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(MultiDeleteTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "POST"
        self.request = self.generate_url("multi_delete")

    def create_form(self):
        return json.dumps(["2044"])

    #######################
    ### Testing methods ###
    #######################

    def test_multi_delete(self):
        expected_response = b'Deleted ids:'
        form_contents = self.create_form()
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
