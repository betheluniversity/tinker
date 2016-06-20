from events_base import EventsBaseTestCase


class ConfirmTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_confirm(self):
        response = self.send_get("/event/confirm")
        assert b'GIF' in response.data
