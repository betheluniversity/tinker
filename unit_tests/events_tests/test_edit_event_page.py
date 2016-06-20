from events_base import EventsBaseTestCase


class EditEventPageTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_edit_event_page(self):
        response = self.send_get("/event/edit_event_page/asdf")
        print "Edit Event Page:", response
        assert b' ' in response.data
