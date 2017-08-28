from sync_controller_base import SyncControllerBaseTestCase


class SyncMetadataSetsTestCase(SyncControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SyncMetadataSetsTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_sync_metadata_sets(self):
        # The reason I have a unit test for sync_metadata_set and not for sync_metadata_sets is because the latter
        # simply calls the former multiple times, effectively duplicating this test.
        pass
