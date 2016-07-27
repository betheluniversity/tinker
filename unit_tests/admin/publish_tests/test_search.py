from publish_base import PublishBaseTestCase


class SearchTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, name, content, metadata, pages, blocks, files, folders):
        csrf_token = super(SearchTestCase, self).get_csrf_token("/admin/publish-manager")
        return {
            'csrf_token': csrf_token,
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
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", "true", "true", "true", "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'<a href="https://cms.bethel.edu/entity/open.act?id=a7404faa8c58651375fc4ed23d7468d5&type=page">/events/arts/galleries/exhibits/2006/projections-and-dreams</a>' in response.data

    def test_search_invalid_name(self):
        form_contents = self.create_form(None, "*This exhibition brings*", "*summary*", "true", "true", "true", "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'<p>The browser (or proxy) sent a request that this server could not understand.</p>' in response.data

    def test_search_invalid_content(self):
        form_contents = self.create_form("*projections-and-dreams*", None, "*summary*", "true", "true", "true", "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'<p>The browser (or proxy) sent a request that this server could not understand.</p>' in response.data

    def test_search_invalid_metadata(self):
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", None, "true", "true", "true", "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'<p>The browser (or proxy) sent a request that this server could not understand.</p>' in response.data

    def test_search_invalid_pages(self):
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", None, "true", "true", "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'<p>The browser (or proxy) sent a request that this server could not understand.</p>' in response.data

    def test_search_invalid_blocks(self):
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", "true", None, "true", "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'<p>The browser (or proxy) sent a request that this server could not understand.</p>' in response.data

    def test_search_invalid_files(self):
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", "true", "true", None, "true")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'<p>The browser (or proxy) sent a request that this server could not understand.</p>' in response.data

    def test_search_invalid_folders(self):
        form_contents = self.create_form("*projections-and-dreams*", "*This exhibition brings*", "*summary*", "true", "true", "true", None)
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'<p>The browser (or proxy) sent a request that this server could not understand.</p>' in response.data
