from events_controller_base import EventsControllerBaseTestCase


class GetCurrentYearFolderTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetCurrentYearFolderTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_current_year_folder_valid(self):
        event_id = '7fd4bfb38c58651360b6175f8a74dd33'
        response = self.controller.get_current_year_folder(event_id)
        self.assertTrue(isinstance(response, int))
        self.assertEqual(response, 2018)

    def test_get_current_year_folder_invalid(self):
        event_id = '0d9e86b88c586513543f13a687e61d4a'
        response = self.controller.get_current_year_folder(event_id)
        self.assertEqual(response, None)
