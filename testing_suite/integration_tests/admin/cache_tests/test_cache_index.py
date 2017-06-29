from testing_suite import BaseTestCase


class IndexTestCase(BaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = self.generate_url("index")

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        expected_response = repr('\xe7\xafN\xad\x08p\x03\x8a\x981\xf9\xe2,V\xd2\xc1')  # b'<div class="large-6 columns">'
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)
