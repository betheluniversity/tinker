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
        form_contents = self.create_form()
        response = super(SearchTestCase, self).send_post('/admin/program-search/search', form_contents)
        assert b'class="program-search-row table-hover">' in response.data
