from unit_tests import BaseTestCase


class MoreInfoTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(MoreInfoTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "POST /admin/publish-manager/more_info"

    def create_form(self, type, id):
        return {
            'type': type,
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_more_info_valid(self):
        expected_response = b'<div class="col-sm-6 last-published-header">'
        form_contents = self.create_form("page", "a7404faa8c58651375fc4ed23d7468d5")
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_more_info_invalid_type(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form(None, "a7404faa8c58651375fc4ed23d7468d5")
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_more_info_invalid_id(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("page", None)
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)