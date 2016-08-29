from cache_base import ClearCacheBaseTestCase


class IndexTestCase(ClearCacheBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        failure_message = '"GET /admin/cache-clear" didn\'t return the HTML code expected by ' + self.class_name + '.'
        expected_response = b'<div class="large-6 columns">'
        response = super(IndexTestCase, self).send_get("/admin/cache-clear")
        self.assertIn(expected_response, response.data, msg=failure_message)
