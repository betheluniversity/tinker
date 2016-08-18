from program_search_base import ProgramSearchBaseTestCase
import json


class MultiDeleteTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(MultiDeleteTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    def create_form(self):
        return json.dumps(["2044"])

    #######################
    ### Testing methods ###
    #######################

    def test_multi_delete(self):
        failure_message = 'Deleting a valid program tag using "POST /admin/program-search/multi-delete" in ' + \
                          self.class_name + ' didn\'t work as expected.'
        expected_response = b'TEST'
        form_contents = self.create_form()
        response = super(MultiDeleteTestCase, self).send_post("/admin/program-search/multi-delete", form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)
