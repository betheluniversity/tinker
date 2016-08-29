from events_base import EventsBaseTestCase


class IndexTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /event" didn\'t return the HTML code expected by ' + class_name + '.'
        expected_response = b'All events will be reviewed and approved within 2-3 business days by Conference'
        response = self.send_get("/event")
        self.assertIn(expected_response, response.data, msg=failure_message)
