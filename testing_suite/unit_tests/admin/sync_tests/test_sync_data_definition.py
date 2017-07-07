from sync_controller_base import SyncControllerBaseTestCase
from tinker import app


class SyncDataDefintionTestCase(SyncControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SyncDataDefintionTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_sync_data_defintion_valid(self):
        # The reason I have a unit test for sync_data_definition and not for sync_data_definitions is because the latter
        # simply calls the former multiple times, effectively duplicating this test.
        data_definition_id = 'yes'
        response = self.controller.sync_data_definition(data_definition_id)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(len(response) == 9)
        # Having it sync a string that isn't a valid data definition ID will return a None
        self.assertTrue(response[0] is None)

    def test_sync_data_defintion_invalid(self):
        # Passing in an invalid ID should make the try/except in this method return an empty list
        data_definition_id = None
        response = self.controller.sync_data_definition(data_definition_id)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(len(response) == 0)
