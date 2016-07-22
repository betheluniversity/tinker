from clear_cache_base import ClearCacheBaseTestCase


class IndexTestCase(ClearCacheBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = self.send_get("/admin/cache-clear")
        assert b'<input type="text" id="cpath"/>' in response.data
