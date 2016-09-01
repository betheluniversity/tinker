from program_search_base import ProgramSearchBaseTestCase
import json


class SearchTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SearchTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "POST /admin/program-search/search"

    def create_form(self):
        return json.dumps({
            "search_key": "athl",
            "search_tag": ""
        })

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        expected_response = b'class="program-search-row table-hover">'
        form_contents = self.create_form()
        response = super(SearchTestCase, self).send_post('/admin/program-search/search', form_contents)
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
