from program_search_base import ProgramSearchBaseTestCase
import json


class SubmitTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SubmitTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

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
        failure_message = 'Sending a valid new form to "POST /admin/program-search/submit" in ' + self.class_name \
                          + ' didn\'t work properly.'
        expected_response = b'<label for="key" style="color: #252422">Concentration Code or Program Name:</label>'
        form_contents = self.create_form()
        response = super(SubmitTestCase, self).send_post('/admin/program-search/submit', form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)
