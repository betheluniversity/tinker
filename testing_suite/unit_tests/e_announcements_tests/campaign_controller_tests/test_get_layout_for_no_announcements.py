from campaign_controller_base import CampaignControllerBaseTestCase


class GetLayoutForNoAnnouncementsTestCase(CampaignControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetLayoutForNoAnnouncementsTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_layout_for_no_announcements(self):
        # Assert that passing in no roles returns no e-annz
        test_roles = []
        expected_response = '<p>There are no E-Announcements for you today.</p>'
        response = self.controller.get_layout_for_no_announcements(test_roles)
        self.assertEqual(expected_response, response)

        # Assert that passing in gibberish roles gives the correct layout
        test_roles = ['foo', 'bar', 'fizz', 'bin']
        expected_response = repr('kr\x02\xe6!\xac\x11b\xec\t\xb4\xee:G\x0e\xfd')
        response = self.controller.get_layout_for_no_announcements(test_roles)
        short_string = self.get_unique_short_string(response)
        self.assertEqual(expected_response, short_string)
