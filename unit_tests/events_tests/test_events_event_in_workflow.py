from unit_tests import BaseTestCase


class EventInWorkflowTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(EventInWorkflowTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /event/event_in_workflow"

    #######################
    ### Testing methods ###
    #######################

    def test_event_in_workflow(self):
        expected_response = b'Edits pending approval'
        response = self.send_get("/event/event_in_workflow")
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)