from unit_tests import BaseTestCase


class InWorkflowTestCase(BaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(InWorkflowTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = self.generate_url("faculty_bio_in_workflow")

    #######################
    ### Testing methods ###
    #######################

    def test_in_workflow(self):
        expected_response = repr('m3G\xf0\xae\x92\xc4\x7f\xdf\xcf\x8b\xa2\xd7\xa3\xaa\x9f')
        # b'<p>You recently made edits to your bio and are currently pending approval. Please wait until'
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)
