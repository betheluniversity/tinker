from program_search_base import ProgramSearchBaseTestCase


class IndexTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        failure_message = '"GET /admin/program-search" didn\'t return the HTML code expected by ' + self.class_name + '.'
        expected_response = b'<label for="key" style="color: #252422">Concentration Code or Program Name:</label>'
        response = super(IndexTestCase, self).send_get("/admin/program-search")
        self.assertIn(expected_response, response.data, msg=failure_message)
