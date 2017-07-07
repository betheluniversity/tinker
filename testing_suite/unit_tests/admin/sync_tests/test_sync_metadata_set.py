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

    def test_sync_metadata_set(self):
        # The reason I have a unit test for sync_metadata_set and not for sync_metadata_sets is because the latter
        # simply calls the former multiple times, effectively duplicating this test.
        metadata_set_id = 'yes'
        response = self.controller.sync_metadata_set(metadata_set_id)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(len(response) == 8)
        # Having it sync a string that isn't a valid metadata set ID will return a None
        self.assertTrue(response[0] is None)
