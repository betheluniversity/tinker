import os

from redirects_controller_base import RedirectsControllerBaseTestCase


class CreateRedirectTextFileTestCase(RedirectsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CreateRedirectTextFileTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_create_new_csv_file(self):
        response = self.controller.create_redirect_text_file()
        self.assertEqual(response, 'done')
        self.assertTrue(os.path.isfile('./redirects.txt'))
        os.remove('./redirects.txt')
        self.assertFalse(os.path.isfile('./redirects.txt'))
        os.remove('./redirects.txt.back')
