from tinker.unit_tests import BaseTestCase


class SearchTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SearchTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "POST /admin/publish-manager/search"

    def create_form(self, name, content, metadata, pages, blocks, files, folders):
        return {
            'name': name,
            'content': content,
            'metadata': metadata,
            'pages': pages,
            'blocks': blocks,
            'files': files,
            'folders': folders
        }

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        expected_response = b'<a href="https://cms.bethel.edu/entity/open.act?id=a7404faa8c58651375fc4ed23d7468d5&type=page">/events/arts/galleries/exhibits/2006/projections-and-dreams</a>'
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", "true", "true", "true", "true")
        response = self.send_post('/admin/publish-manager/search', form_contents)
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_name(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form(None, "*This exhibition brings*", "*summary*", "true", "true", "true", "true")
        response = self.send_post('/admin/publish-manager/search', form_contents)
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_content(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", None, "*summary*", "true", "true", "true", "true")
        response = self.send_post('/admin/publish-manager/search', form_contents)
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_metadata(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", None, "true", "true", "true", "true")
        response = self.send_post('/admin/publish-manager/search', form_contents)
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_pages(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", None, "true", "true", "true")
        response = self.send_post('/admin/publish-manager/search', form_contents)
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_blocks(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", "true", None, "true", "true")
        response = self.send_post('/admin/publish-manager/search', form_contents)
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_files(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", "true", "true", None, "true")
        response = self.send_post('/admin/publish-manager/search', form_contents)
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_folders(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", "true", "true", "true", None)
        response = self.send_post('/admin/publish-manager/search', form_contents)
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
