from tinker_controller_base import TinkerControllerBaseTestCase


class EscapeXMLIllegalCharactersTestCase(TinkerControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(EscapeXMLIllegalCharactersTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_escape_xml_illegal_characters(self):
        test_value = u'\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF'
        self.assertTrue(isinstance(test_value, unicode))
        self.assertEqual(test_value, '?-????-??-???')
