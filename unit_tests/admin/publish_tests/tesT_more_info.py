from publish_base import PublishBaseTestCase


class MoreInfoTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, type, id):
        return {
            'type': type,
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_more_info_valid(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = 'Sending a valid form to "POST /admin/publish-manager/more_info" in ' + class_name \
                          + ' failed unexpectedly.'
        form_contents = self.create_form("page", "a7404faa8c58651375fc4ed23d7468d5")
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        self.assertIn(b'<h4>WWW last published</h4>', response.data, msg=failure_message)
        # assert b'</tr>\
        #     </table>\
        #     \
        #     <div class="row">\
        #     \
        #     <div class="large-6 columns">\
        #     <h4>WWW last published</h4>' in response.data

    def test_more_info_invalid_type(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = 'Sending an invalid \'type\' to "POST /admin/publish-manager/more_info" in ' + class_name \
                          + ' didn\'t fail in the expected way.'
        form_contents = self.create_form(None, "a7404faa8c58651375fc4ed23d7468d5")
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        self.assertIn(b'<p>The browser (or proxy) sent a request that this server could not understand.</p>', response.data, msg=failure_message)

    def test_more_info_invalid_id(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = 'Sending an invalid \'id\' to "POST /admin/publish-manager/more_info" in ' + class_name \
                          + ' didn\'t fail in the expected way.'
        form_contents = self.create_form("page", None)
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        self.assertIn(b'<p>The browser (or proxy) sent a request that this server could not understand.</p>', response.data, msg=failure_message)