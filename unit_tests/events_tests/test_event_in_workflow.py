from events_base import EventsBaseTestCase

class EventInWorkflowTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_event_in_workflow(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /event/event_in_workflow" didn\'t return the HTML code expected by ' + class_name + '.'
        response = self.send_get("/event/event_in_workflow")
        self.assertIn(b'Edits pending approval', response.data, msg=failure_message)