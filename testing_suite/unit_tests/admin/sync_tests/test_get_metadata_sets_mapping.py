from sync_controller_base import SyncControllerBaseTestCase


class GetMetaDataSetsMappingTestCase(SyncControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetMetaDataSetsMappingTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_metadata_sets_mapping(self):
        response = self.controller.get_metadata_sets_mapping()
        self.assertTrue(isinstance(response, dict))
        expected_values = [
            'Event',
            'Robust',
            'Job Posting'
        ]
        for key in response.keys():
            self.assertTrue(isinstance(key, str))
            self.assertTrue(len(key) == 32)
            self.assertTrue(response[key] in expected_values)
