from . import RedirectsBaseTestCase


class IndexTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index_valid(self):
        response = self.send_get("/admin/redirect")
        assert b'<th width="400">From Path</th>' in response.data