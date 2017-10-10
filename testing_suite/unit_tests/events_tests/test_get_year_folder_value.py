from events_controller_base import EventsControllerBaseTestCase


class GetYearFolderValueTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetYearFolderValueTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_year_folder_value(self):
        test_data = {
            'event-dates': [{
                'end-date': self.controller.date_str_to_timestamp('August 3 2017, 11:00 am')
            }]
        }
        response = self.controller.get_year_folder_value(test_data)
        self.assertTrue(isinstance(response, int))
        self.assertEqual(response, 2017)
