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
        response = self.controller.__html_entities_to_unicode__(test_text)
        self.assertTrue(isinstance(response, unicode))
        self.assertEqual(response, u'<p>123&4</p>')
