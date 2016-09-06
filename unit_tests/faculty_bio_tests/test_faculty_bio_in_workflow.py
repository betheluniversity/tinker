from unit_tests import BaseTestCase


class InWorkflowTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(InWorkflowTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /faculty-bio/in-workflow"

    #######################
    ### Testing methods ###
    #######################

    def test_in_workflow(self):
        expected_response = b'<p>You recently made edits to your bio and are currently pending approval. Please wait until the changes have been approved before you make additional edits. Go back to your'
        response = self.send_get("/faculty-bio/in-workflow")
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
