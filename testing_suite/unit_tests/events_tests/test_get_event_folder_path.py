from events_controller_base import EventsControllerBaseTestCase


class GetEventFolderPathTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetEventFolderPathTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_event_folder_path(self):
        # Because the config variable UNIT_TESTING should be true when this is run, it shouldn't matter what gets passed
        # into this method, it should always return the same path.
        test_data = {
            'event-dates': []
        }
        response = self.controller.get_event_folder_path(test_data)
        self.assertTrue(isinstance(response, tuple))
        self.assertEqual(len(response), 2)
        self.assertTrue(isinstance(response[0], str))
        self.assertEqual(response[0], 'Hide')
        self.assertTrue(isinstance(response[1], str))
        self.assertEqual(response[1], '/_testing/philip-gibbens/events-tests')
