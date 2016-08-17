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
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = 'Sending a valid new form to "POST /admin/program-search/subit" in ' + class_name \
                          + ' didn\'t work properly.'
        form_contents = self.create_form()
        response = super(SubmitTestCase, self).send_post('/admin/program-search/submit', form_contents)
        self.assertIn(b'<p>Below is the list of Office Hours you have access to edit.', response.data, msg=failure_message)
