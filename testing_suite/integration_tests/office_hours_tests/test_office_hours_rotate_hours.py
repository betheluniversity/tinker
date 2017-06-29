from testing_suite import BaseTestCase


class RotateHoursTestCase(BaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(RotateHoursTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = ""

    #######################
    ### Testing methods ###
    #######################

    def test_rotate_hours(self):
        # block_id = "4f78feca8c58651305d79299fb5aa2bb"
        # self.request = self.generate_url("rotate_hours", block_id=block_id)
        # expected_response = b'success'
        # response = self.send_get(self.request)
        # failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
        #                                                 expected_response, self.class_name, self.get_line_number())
        # self.assertIn(expected_response, response.data, msg=failure_message)
        pass
