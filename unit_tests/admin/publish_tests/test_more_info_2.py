from publish_base import PublishBaseTestCase


class MoreInfoTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(MoreInfoTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    def create_form(self, type, id):
        return {
            'type': type,
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_more_info_valid(self):
        failure_message = 'Sending a valid form to "POST /admin/publish-manager/more_info" in ' + self.class_name \
                          + ' failed unexpectedly.'
        expected_response = b'<div class="col-sm-6 last-published-header">'
        form_contents = self.create_form("page", "a7404faa8c58651375fc4ed23d7468d5")
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_more_info_invalid_type(self):
        failure_message = 'Sending an invalid \'type\' to "POST /admin/publish-manager/more_info" in ' + self.class_name \
                          + ' didn\'t fail in the expected way.'
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form(None, "a7404faa8c58651375fc4ed23d7468d5")
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_more_info_invalid_id(self):
        failure_message = 'Sending an invalid \'id\' to "POST /admin/publish-manager/more_info" in ' + self.class_name \
                          + ' didn\'t fail in the expected way.'
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form("page", None)
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)