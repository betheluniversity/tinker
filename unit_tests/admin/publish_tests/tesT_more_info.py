from . import PublishBaseTestCase


class MoreInfoTestCase(PublishBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_more_info_valid(self):
        form_contents = {'type': "yes",
                         'id': "no"}
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        assert b'</tr>\
            </table>\
            \
            <div class="row">\
            \
            <div class="large-6 columns">\
            <h4>WWW last published</h4>' in response.data

    def test_more_info_invalid_type(self):
        form_contents = {'type': None,
                         'id': "no"}
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        assert b'400 Bad Request' in response.data

    def test_more_info_invalid_id(self):
        form_contents = {'type': "yes",
                         'id': None}
        response = super(MoreInfoTestCase, self).send_post('/admin/publish-manager/more_info', form_contents)
        assert b'400 Bad Request' in response.data