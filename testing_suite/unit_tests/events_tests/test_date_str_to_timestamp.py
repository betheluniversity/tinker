from events_controller_base import EventsControllerBaseTestCase


class DateStringToTimestampTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(DateStringToTimestampTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_date_str_to_timestamp_valid(self):
        test_date_string = 'August 7 2017, 11:00 am'
        response = self.controller.date_str_to_timestamp(test_date_string)
        self.assertTrue(isinstance(response, int))
        # Because the timezones being used by our machines and the Travis CI machines are different, I can't assert
        # that the timestamp provided has a particular value.
        # TODO

    def test_date_str_to_timestamp_invalid(self):
        test_date_string = 'gibberish'
        self.assertRaises(ValueError, self.controller.date_str_to_timestamp, test_date_string)
