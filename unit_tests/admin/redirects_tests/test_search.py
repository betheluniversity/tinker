from redirects_base import RedirectsBaseTestCase


class SearchTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, search_type, search):
        csrf_token = super(SearchTestCase, self).get_csrf_token('/admin/redirect')
        return {
            'csrf_token': csrf_token,
            'type': search_type,
            'search': search
        }

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        form_contents = self.create_form("from_path", "/")
        response = super(SearchTestCase, self).send_post('/admin/redirect/search', form_contents)
        assert b'<span class="from_path">' in response.data

    def test_search_invalid_type(self):
        form_contents = self.create_form(None, "/")
        response = super(SearchTestCase, self).send_post('/admin/redirect/search', form_contents)
        assert b'400 Bad Request' in response.data

    def test_search_invalid_term(self):
        form_contents = self.create_form("from_path", None)
        response = super(SearchTestCase, self).send_post('/admin/redirect/search', form_contents)
        assert b'400 Bad Request' in response.data