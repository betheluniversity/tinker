from events_base import EventsBaseTestCase


class DuplicateEventPageTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_duplicate_event_page(self):
        response = self.send_get("/event/duplicate_event_page/adsf")
        assert b' ' in response.data
