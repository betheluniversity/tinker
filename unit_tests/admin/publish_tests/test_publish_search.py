from publish_base import PublishBaseTestCase


class SearchTestCase(PublishBaseTestCase):
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
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_name(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form(None, "*This exhibition brings*", "*summary*", "true", "true", "true", "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_content(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", None, "*summary*", "true", "true", "true", "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_metadata(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", None, "true", "true", "true", "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_pages(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", None, "true", "true", "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_blocks(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", "true", None, "true", "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_files(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", "true", "true", None, "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_search_invalid_folders(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", "true", "true", "true", None)
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)
