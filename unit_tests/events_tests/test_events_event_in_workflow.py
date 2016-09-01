from unit_tests import BaseTestCase


class EventInWorkflowTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(EventInWorkflowTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_event_in_workflow(self):
        failure_message = '"GET /event/event_in_workflow" didn\'t return the HTML code expected by ' + self.class_name + '.'
        expected_response = b'Edits pending approval'
        response = self.send_get("/event/event_in_workflow")
        self.assertIn(expected_response, response.data, msg=failure_message)