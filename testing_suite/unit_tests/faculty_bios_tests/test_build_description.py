from faculty_bios_controller_base import FacultyBiosControllerBaseTestCase


class BuildDescriptionTestCase(FacultyBiosControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(BuildDescriptionTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_build_description(self):
        expected_response = repr("\xd7'G\xa6w\xa93F\x9b\xbf\xd2V\x08\xd0\xce\n")
        test_add_data = {
            'first': 'Philip',
            'last': 'Gibbens',
            'schools1': 'Bethel University',
            'new-job-title1': 'Conqueror of All'
        }
        response = self.controller.build_description(test_add_data)
        short_string = self.get_unique_short_string(response)
        self.assertEqual(short_string, expected_response)
