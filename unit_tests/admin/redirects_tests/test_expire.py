from redirects_base import RedirectsBaseTestCase


class ExpireTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_expire(self):
        response = super(ExpireTestCase, self).send_get('/admin/redirect/expire')
        assert b'done' in response.data
