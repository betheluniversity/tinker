from redirects_base import RedirectsBaseTestCase


class TestingTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_the_test(self):
        response = self.send_get("/admin/redirect/test")
        assert b'<pre>' in response.data
