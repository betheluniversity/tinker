from tinker_controller_base import TinkerControllerBaseTestCase


class EscapeWYSIWYGContentTestCase(TinkerControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(EscapeWYSIWYGContentTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_escape_wysiwyg_content(self):
        test_content = u'<p>asdf</p>'
        expected_response = '<p>asdf</p>'
        response = self.controller.escape_wysiwyg_content(test_content)
        self.assertTrue(isinstance(response, unicode))
        self.assertEqual(response, expected_response)
