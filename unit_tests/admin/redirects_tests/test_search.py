from redirects_base import RedirectsBaseTestCase


class SearchTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, search_type, search):
        return {
            'type': search_type,
            'search': search
        }

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = 'Sending a valid search to "POST /admin/redirect/search" didn\'t succeed when it should have in ' + class_name + '.'
        form_contents = self.create_form("from_path", "/")
        response = super(SearchTestCase, self).send_post('/admin/redirect/search', form_contents)
        self.assertIn(b'<span class="from_path">', response.data, msg=failure_message)

    def test_search_invalid_type(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = 'Sending an invalid "type" to "POST /admin/redirect/search" didn\'t fail as expected in ' + class_name + '.'
        form_contents = self.create_form(None, "/")
        response = super(SearchTestCase, self).send_post('/admin/redirect/search', form_contents)
        self.assertIn(b'400 Bad Request', response.data, msg=failure_message)

    def test_search_invalid_term(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = 'Sending an invalid "term" to "POST /admin/redirect/search" didn\'t fail as expected in ' + class_name + '.'
        form_contents = self.create_form("from_path", None)
        response = super(SearchTestCase, self).send_post('/admin/redirect/search', form_contents)
        self.assertIn(b'400 Bad Request', response.data, msg=failure_message)