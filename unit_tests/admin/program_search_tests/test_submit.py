from program_search_base import ProgramSearchBaseTestCase
import json


class SubmitTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self):
        return json.dumps({
            'key': "x",
            'tag': "z",
            'outcome': "False",
            'topic': "False",
            'other': "False"
        })

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        form_contents = self.create_form()
        response = super(SubmitTestCase, self).send_post('/admin/program-search/submit', form_contents)
        assert b'<p>Below is the list of Office Hours you have access to edit.' in response.data
