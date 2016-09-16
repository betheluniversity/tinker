from redirects_base import RedirectsBaseTestCase


class SearchTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SearchTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "POST"
        self.request = self.generate_url("search")

    def create_form(self, search_type, search):
        return {
            'type': search_type,
            'search': search
        }

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        expected_response = b'<span class="from_path">'
        form_contents = self.create_form("from_path", "/")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_type(self):
        expected_response = self.ERROR_400
        form_contents = self.create_form(None, "/")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_term(self):
        expected_response = self.ERROR_400
        form_contents = self.create_form("from_path", None)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)