from program_search_base import ProgramSearchBaseTestCase


class SubmitTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self):
        csrf_token = super(SubmitTestCase, self).get_csrf_token('/admin/program-search')
        return {
            'csrf_token': csrf_token,
            'key': "x",
            'tag': "z",
            'outcome': "False",
            'topic': "False",
            'other': "False"
        }

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        form_contents = self.create_form()
        response = super(SubmitTestCase, self).send_post('/admin/program-search/submit', form_contents)
        assert b'<input type="text" name="key" id=\'search-key\' class=\'search-input\' placeholder="Filter Key" />' in response.data
