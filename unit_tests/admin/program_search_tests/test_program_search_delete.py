from program_search_base import ProgramSearchBaseTestCase
import json


class MultiDeleteTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(MultiDeleteTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "POST /admin/program-search/multi-delete"

    def create_form(self):
        return json.dumps(["2044"])

    #######################
    ### Testing methods ###
    #######################

    def test_multi_delete(self):
        expected_response = b'Deleted ids:'
        form_contents = self.create_form()
        response = super(MultiDeleteTestCase, self).send_post("/admin/program-search/multi-delete", form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)
