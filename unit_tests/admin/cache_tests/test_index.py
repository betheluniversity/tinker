from cache_base import ClearCacheBaseTestCase


class IndexTestCase(ClearCacheBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /admin/cache-clear" didn\'t return the HTML code expected by ' + class_name + '.'
        response = super(IndexTestCase, self).send_get("/admin/cache-clear")
        self.assertIn(b'<div class="large-6 columns">', response.data, msg=failure_message)
