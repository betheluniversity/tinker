from program_search_base import ProgramSearchBaseTestCase


class IndexTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /admin/program-search" didn\'t return the HTML code expected by ' + class_name + '.'
        response = super(IndexTestCase, self).send_get("/admin/program-search")
        self.assertIn(b'<p>Below is the list of Office Hours you have access to edit.', response.data, msg=failure_message)
