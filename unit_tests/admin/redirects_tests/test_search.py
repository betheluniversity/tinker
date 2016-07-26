from redirects_base import RedirectsBaseTestCase


class SearchTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        form_contents = {'type': "from_path",
                         'search': "/"}
        response = super(SearchTestCase, self).send_post('/admin/redirect/search', form_contents)
        assert b'<span class="from_path">' in response.data

    def test_search_invalid_type(self):
        form_contents = {'type': None,
                         'search': "/"}
        response = super(SearchTestCase, self).send_post('/admin/redirect/search', form_contents)
        assert b'400 Bad Request' in response.data

    def test_search_invalid_term(self):
        form_contents = {'type': "from_path",
                         'search': None}
        response = super(SearchTestCase, self).send_post('/admin/redirect/search', form_contents)
        assert b'400 Bad Request' in response.data