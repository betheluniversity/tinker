import json
from program_search_base import ProgramSearchBaseTestCase


class SearchTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self):
        return json.dumps({
            "search_key": "athl",
            "search_tag": ""
        })

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = 'Sending a valid search to "POST /admin/program-search/search" in ' + class_name \
                          + ' didn\'t work properly.'
        form_contents = self.create_form()
        response = super(SearchTestCase, self).send_post('/admin/program-search/search', form_contents)
        self.assertIn(b'class="program-search-row table-hover">', response.data, msg=failure_message)
