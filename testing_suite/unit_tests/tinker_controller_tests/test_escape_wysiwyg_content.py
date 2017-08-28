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
        test_content = u'<div>asdf</div>'
        expected_response = '&lt;p&gt;asdf&lt;/p&gt;'
        response = self.controller.escape_wysiwyg_content(test_content)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, expected_response)
