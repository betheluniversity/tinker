from sync_controller_base import SyncControllerBaseTestCase


class GetDataDefinitionsMappingTestCase(SyncControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetDataDefinitionsMappingTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_data_defintions_mapping(self):
        response = self.controller.get_data_definitions_mapping()
        self.assertTrue(isinstance(response, dict))
        expected_values = [
            'Program',
<<<<<<< HEAD
            'Tab',
=======
            'Page',
>>>>>>> master
            'Channel Block',
            'Program Feed',
            'Faculty Bio'
        ]
        for key in response.keys():
            self.assertTrue(isinstance(key, str))
            self.assertEqual(len(key), 32)
            self.assertTrue(response[key] in expected_values)
