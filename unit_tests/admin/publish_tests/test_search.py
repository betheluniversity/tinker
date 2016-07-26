from publish_base import PublishBaseTestCase


class SearchTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

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
        form_contents = self.create_form("", "", "", "", "", "", "")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'<tr><td>' in response.data

    def test_search_invalid_name(self):
        form_contents = self.create_form(None, "", "", "", "", "", "")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'400 Bad Request' in response.data

    def test_search_invalid_content(self):
        form_contents = self.create_form("", None, "", "", "", "", "")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'400 Bad Request' in response.data

    def test_search_invalid_metadata(self):
        form_contents = self.create_form("", "", None, "", "", "", "")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'400 Bad Request' in response.data

    def test_search_invalid_pages(self):
        form_contents = self.create_form("", "", "", None, "", "", "")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'400 Bad Request' in response.data

    def test_search_invalid_blocks(self):
        form_contents = self.create_form("", "", "", "", None, "", "")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'400 Bad Request' in response.data

    def test_search_invalid_files(self):
        form_contents = self.create_form("", "", "", "", "", None, "")
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'400 Bad Request' in response.data

    def test_search_invalid_folders(self):
        form_contents = self.create_form("", "", "", "", "", "", None)
        response = super(SearchTestCase, self).send_post('/admin/publish-manager/search', form_contents)
        assert b'400 Bad Request' in response.data
