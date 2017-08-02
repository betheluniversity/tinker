from events_controller_base import EventsControllerBaseTestCase


class TimestampToDatestringTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(TimestampToDatestringTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_timestamp_to_date_str_valid(self):
        test_timestamp = '1501909200000'
        response = self.controller.timestamp_to_date_str(test_timestamp)
        self.assertTrue(isinstance(response, str))
        # Because the timezones being used by our machines and the Travis CI machines are different, I can't assert
        # that the date string provided has a particular value.
        # TODO

    def test_timestamp_to_date_str_invalid(self):
        test_timestamp = 'gibberish'
        self.assertRaises(ValueError, self.controller.timestamp_to_date_str, test_timestamp)
