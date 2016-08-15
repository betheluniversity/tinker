from program_search_base import ProgramSearchBaseTestCase
import json


class MultiDeleteTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self):
        return json.dumps(["2044"])

    #######################
    ### Testing methods ###
    #######################

    def test_multi_delete(self):
        form_contents = self.create_form()
        response = super(MultiDeleteTestCase, self).send_post("/admin/program-search/multi-delete", form_contents)
        assert b'TEST' in response.data
