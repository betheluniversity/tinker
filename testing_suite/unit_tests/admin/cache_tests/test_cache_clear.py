from cache_controller_base import CacheControllerBaseTestCase


class CacheClearTestCase(CacheControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CacheClearTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_cache_clear_valid(self):
        img_path = "/foo"
        response = self.controller.cache_clear(img_path)
        self.assertEqual(response, 'Cache cleared for path, "%s"' % img_path)

    def test_cache_clear_invalid(self):
        img_path = None
        response = self.controller.cache_clear(img_path)
        self.assertEqual(response, "Please enter in a path.")
