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
        response = self.send_get("/event")
        self.assertIn(b'within 2-3 business days by Conference and Event Services.', response.data, msg=failure_message)
