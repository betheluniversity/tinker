from sync_controller_base import SyncControllerBaseTestCase


class SyncDataDefinitionTestCase(SyncControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SyncDataDefinitionTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_sync_data_definition_valid(self):
        # The reason I have a unit test for sync_data_definition and not for sync_data_definitions is because the latter
        # simply calls the former multiple times, effectively duplicating this test.
        data_definition_id = 'yes'
        response = self.controller.sync_data_definition(data_definition_id)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), 9)
        # Having it sync a string that isn't a valid data definition ID will return a None
        self.assertTrue(response[0] is None)

    def test_sync_data_definition_invalid(self):
        # Passing in an invalid ID should make the try/except in this method return an empty list
        data_definition_id = None
        response = self.controller.sync_data_definition(data_definition_id)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), 0)
