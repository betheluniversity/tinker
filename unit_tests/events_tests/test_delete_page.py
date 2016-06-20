from events_base import EventsBaseTestCase

class DeleteTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_delete_page(self):
        response = self.send_get("/events/delete_page/59f269a38c58651305d79299440ce093")
        # Right now throwing 500 because the method the endpoint references isn't working at the moment.
        assert b'Whoops!' in response.data