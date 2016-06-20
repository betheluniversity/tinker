from events_base import EventsBaseTestCase


class IndexTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = self.send_get("/event")
        assert b'within 2-3 business days by Conference and Event Services.' in response.data
