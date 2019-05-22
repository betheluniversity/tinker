from redirects_base import RedirectsBaseTestCase


class SearchTestCase(RedirectsBaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SearchTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("search")

    def create_form(self, from_path='/about', to_url='https://www.bethel.edu/about/'):
        return {
            'from_path': from_path,
            'to_url': to_url
        }

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        expected_response = repr('\x00\xb0\xd3H&0\x9b\xfd?s-\x99\x11Qa\xd7')  # b'<span class="from_path">'
        form = self.create_form()
        response = self.send_post(self.request, form)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, short_string, msg=failure_message)

    def test_search_invalid(self):
        expected_response = ""
        arg_names = ['from_path', 'to_url']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: ''}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/search_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertIn(expected_response, response.data, msg=failure_message)
