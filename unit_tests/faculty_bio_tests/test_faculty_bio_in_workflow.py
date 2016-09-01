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
        response = super(InWorkflowTestCase, self).send_get("/faculty-bio/in-workflow")
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)
