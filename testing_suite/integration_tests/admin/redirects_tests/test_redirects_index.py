from redirects_base import RedirectsBaseTestCase


class IndexTestCase(RedirectsBaseTestCase):

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
        expected_response = repr('\xe8\x9c\xbb}\x18\x94fQ%\xa6\\d{\xab\xda\xaa')
        # b'<form action="" id="new-redirect-form">'
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertEqual(expected_response, short_string, msg=failure_message)