from campaign_controller_base import CampaignControllerBaseTestCase
from tinker import app


class EAnnouncementHTMLTestCase(CampaignControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(EAnnouncementHTMLTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_e_announcement_html(self):
        dummy_announcement = {
            'title': 'Behold, mimicry',
            'message': 'This dictionary is designed to mimic the structure of a proper e-annz for testing purposes'
        }
        with app.app_context():
            expected_response = repr('\xd4\x1d\x8c\xd9\x8f\x00\xb2\x04\xe9\x80\t\x98\xec\xf8B~')
            response = self.controller.e_announcement_html(dummy_announcement)
            short_string = self.get_unique_short_string(response)
            self.assertEqual(expected_response, short_string)
