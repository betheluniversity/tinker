import json
from program_search_base import ProgramSearchBaseTestCase


class SearchTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SearchTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("search")

    def create_form(self, search_key, search_tag):
        return json.dumps({
            "search_key": search_key,
            "search_tag": search_tag
        })

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        expected_response = b'class="program-search-row table-hover">'
        form_contents = self.create_form("athl", "")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
