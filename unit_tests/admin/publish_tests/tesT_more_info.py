from publish_base import PublishBaseTestCase


class MoreInfoTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, type, id):
        csrf_token = super(MoreInfoTestCase, self).get_csrf_token("/admin/publish-manager")
        return {
            'csrf_token': csrf_token,
            'type': type,
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_more_info_valid(self):
        form_contents = self.create_form("page", "a7404faa8c58651375fc4ed23d7468d5")
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        assert b'<h4>WWW last published</h4>' in response.data
        # assert b'</tr>\
        #     </table>\
        #     \
        #     <div class="row">\
        #     \
        #     <div class="large-6 columns">\
        #     <h4>WWW last published</h4>' in response.data

    def test_more_info_invalid_type(self):
        form_contents = self.create_form(None, "a7404faa8c58651375fc4ed23d7468d5")
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        assert b'<p>The browser (or proxy) sent a request that this server could not understand.</p>' in response.data

    def test_more_info_invalid_id(self):
        form_contents = self.create_form("page", None)
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        assert b'<p>The browser (or proxy) sent a request that this server could not understand.</p>' in response.data