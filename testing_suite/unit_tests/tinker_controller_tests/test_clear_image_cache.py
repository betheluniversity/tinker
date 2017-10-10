from tinker_controller_base import TinkerControllerBaseTestCase


class ClearImageCacheTestCase(TinkerControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ClearImageCacheTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_clear_image_cache_valid(self):
        img_path = "/foo"
        expected_response = str(['/00/29c4d66522ff8cf655a9d69e26deaa171ed152',
                                 '/46/e1b4a852f6488b74622add463e712ea6cfedaa',
                                 '/87/623725ac9c1fded1a6b66eb43ee326bd285d1c',
                                 '/84/893b799c5a1c66b8752977b3a0c9757bc60e68'])
        response = self.controller.clear_image_cache(img_path)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, expected_response)

    def test_clear_image_cache_invalid(self):
        img_path = None
        self.assertRaises(AttributeError, self.controller.clear_image_cache, img_path)
