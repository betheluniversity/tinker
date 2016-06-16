from events_base import EventsBaseTestCase

class EventInWorkflowTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_event_in_workflow(self):
        response = self.send_get("/event/event-in-workflow")
        print response
        # print response.data
        assert b' ' in response.data