from tinker_controller_base import TinkerControllerBaseTestCase


class UnicodeToHTMLEntitiesTestCase(TinkerControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(UnicodeToHTMLEntitiesTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_unicode_to_html_entities(self):
        test_text = u'<p>123&4</p>'
        self.assertTrue(isinstance(test_text, str))
        self.assertEqual(test_text, '&lt;p&gt;123&amp;4&lt;/p&gt;')
