from events_base import EventsBaseTestCase


class HomeTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_home(self):
        response = self.send_get("/events/home")
        assert b'within 2-3 business days by Conference and Event Services.' in response.data
