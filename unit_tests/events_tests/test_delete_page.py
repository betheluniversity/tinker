from events_base import EventsBaseTestCase

class DeleteTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_delete_page(self):
        response = self.send_get("/events/delete-page")   # /59f269a38c58651305d79299440ce093")
        # print response
        # print response.data
        # assert b'Your event has been deleted.' in response.data