from e_annz_controller_base import EAnnouncementsControllerBaseTestCase


class GetEAnnouncementParentFolderTestCase(EAnnouncementsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetEAnnouncementParentFolderTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_e_announcement_parent_folder(self):
        test_date_valid = '08-01-2017'
        expected_response = '/e-announcements/2017/august'
        response = self.controller.get_e_announcement_parent_folder(test_date_valid)
        self.assertEqual(expected_response, response)

        test_date_invalid = '08/01/2017'
        self.assertRaises(ValueError, self.controller.get_e_announcement_parent_folder, test_date_invalid)

        test_date_invalid = '8-2017'
        self.assertRaises(IndexError, self.controller.get_e_announcement_parent_folder, test_date_invalid)

        test_date_invalid = 'gibberish'
        self.assertRaises(ValueError, self.controller.get_e_announcement_parent_folder, test_date_invalid)
