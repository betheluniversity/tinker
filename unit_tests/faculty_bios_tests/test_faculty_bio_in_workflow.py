from unit_tests import BaseTestCase


class InWorkflowTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(InWorkflowTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "GET"
        self.request = self.generate_url("faculty_bio_in_workflow")

    #######################
    ### Testing methods ###
    #######################

    def test_in_workflow(self):
        expected_response = b'<p>You recently made edits to your bio and are currently pending approval. Please wait until'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)