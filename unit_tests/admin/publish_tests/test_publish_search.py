from unit_tests import BaseTestCase


class SearchTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SearchTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "POST"
        self.request = self.generate_url("search")

    def create_form(self, files, folders, blocks, name, content, pages, metadata):
        return {
            'files': files,
            'folders': folders,
            'blocks': blocks,
            'name': name,
            'content': content,
            'pages': pages,
            'metadata': metadata
        }

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        expected_response = b'<tr class="publish-table">'
        form_contents = self.create_form("true", "true", "true", "*projections-and-dreams*", "*This exhibition brings*", "true", "*summary*")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_search_invalid_files(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form(None, "true", "true", "*projections-and-dreams*", "*This exhibition brings*", "true", "*summary*")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_search_invalid_folders(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("true", None, "true", "*projections-and-dreams*", "*This exhibition brings*", "true", "*summary*")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_search_invalid_blocks(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("true", "true", None, "*projections-and-dreams*", "*This exhibition brings*", "true", "*summary*")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_search_invalid_name(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("true", "true", "true", None, "*This exhibition brings*", "true", "*summary*")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_search_invalid_content(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("true", "true", "true", "*projections-and-dreams*", None, "true", "*summary*")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_search_invalid_pages(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("true", "true", "true", "*projections-and-dreams*", "*This exhibition brings*", None, "*summary*")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_search_invalid_metadata(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form("true", "true", "true", "*projections-and-dreams*", "*This exhibition brings*", "true", None)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
