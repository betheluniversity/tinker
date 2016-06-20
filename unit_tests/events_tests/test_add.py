from events_base import EventsBaseTestCase


class AddTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_add(self):
        response = self.send_get("/events/add")
        assert b'please contact Conference and Event Services' in response.data
