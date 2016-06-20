from events_base import EventsBaseTestCase


class SudmitEditFormTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_submit_edit_form(self):
        response = self.send_get("/events/submit_edit_form")
        assert b' ' in response.data
