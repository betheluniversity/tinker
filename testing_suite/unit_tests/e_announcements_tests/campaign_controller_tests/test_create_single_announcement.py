from campaign_controller_base import CampaignControllerBaseTestCase
from tinker import app


class CreateSingleAnnouncementTestCase(CampaignControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CreateSingleAnnouncementTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_create_single_announcement(self):
        dummy_announcement = {
            'title': 'Behold, mimicry',
            'message': 'This dictionary is designed to mimic the structure of a proper e-annz for testing purposes',
            'roles': ['dinner', 'kaiser', 'croissant']
        }
        with app.app_context():
            response = self.controller.create_single_announcement(dummy_announcement)
            # print response
