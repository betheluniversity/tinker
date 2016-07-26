from . import RedirectsBaseTestCase


class ExpireTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_expire(self):
        response = self.send_get('/admin/redirect/expire')
        assert b'done' in response.data
