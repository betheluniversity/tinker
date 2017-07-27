from sync_controller_base import SyncControllerBaseTestCase


class SyncMetadataSetTestCase(SyncControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SyncMetadataSetTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_sync_metadata_set_valid(self):
        # The reason I have a unit test for sync_metadata_set and not for sync_metadata_sets is because the latter
        # simply calls the former multiple times, effectively duplicating this test.
        metadata_set_id = 'yes'
        response = self.controller.sync_metadata_set(metadata_set_id)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), 8)
        # Having it sync a string that isn't a valid metadata set ID will return a None
        self.assertTrue(response[0] is None)

    def test_sync_metadata_set_invalid(self):
        # Passing in an invalid ID should make the try/except in this method return an empty list
        metadata_set_id = None
        response = self.controller.sync_metadata_set(metadata_set_id)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), 0)
