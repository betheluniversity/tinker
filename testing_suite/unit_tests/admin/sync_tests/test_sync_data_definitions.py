from sync_controller_base import SyncControllerBaseTestCase


class SyncDataDefinitionsTestCase(SyncControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SyncDataDefinitionsTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_sync_data_definitions(self):
        # The reason I have a unit test for sync_data_definition and not for sync_data_definitions is because the latter
        # simply calls the former multiple times, effectively duplicating this test.
        pass
