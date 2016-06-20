from events_base import EventsBaseTestCase

class DeleteTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_delete_page(self):
        response = self.send_get("/event/delete/59f269a38c58651305d79299440ce093")
        assert b'Whoops!' in response.data