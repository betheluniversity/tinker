from tinker_controller_base import TinkerControllerBaseTestCase


class HTMLEntitiesToUnicodeTestCase(TinkerControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(HTMLEntitiesToUnicodeTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_html_entities_to_unicode(self):
        test_text = '&lt;p&gt;123&amp;4&lt;/p&gt;'
        self.assertTrue(isinstance(test_text, unicode))
        self.assertEqual(test_text, u'<p>123&4</p>')
