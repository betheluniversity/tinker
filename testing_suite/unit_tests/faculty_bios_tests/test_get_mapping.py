from faculty_bios_controller_base import FacultyBiosControllerBaseTestCase


class GetMappingTestCase(FacultyBiosControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetMappingTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_mapping(self):
        expected_keys = ['Anthropology, Sociology, & Reconciliation', 'Art & Design', 'Biblical & Theological Studies',
                         'Biological Sciences', 'Business & Economics', 'Chemistry', 'Communication Studies',
                         'Doctor of Ministry', 'Education', 'English', 'Environmental Studies', 'General Education',
                         'History', 'Honors', 'Human Kinetics & Applied Health Science', 'Math & Computer Science',
                         'Music', 'Nursing', 'Philosophy', 'Physics & Engineering', 'Political Science', 'Psychology',
                         'Social Work', 'Theatre Arts', 'World Languages and Cultures']
        expected_values = ['Anthropology Sociology', 'Art', 'Biblical Theological', 'Biology', 'Business Economics',
                           'Chemistry', 'Communication', 'Doctor of Ministry', 'Education', 'English',
                           'Environmental Studies','General Education', 'History', 'Honors', 'Human Kinetics',
                           'Math CS', 'Music', 'Nursing', 'Philosophy', 'Physics', 'Political Science', 'Psychology',
                           'Social Work', 'Theatre', 'World Languages']
        response = self.controller.get_mapping()
        self.assertTrue(isinstance(response, dict))
        self.assertEqual(len(response.keys()), len(expected_keys))
        for key in response.keys():
            self.assertTrue(key in expected_keys)
            self.assertTrue(response[key] in expected_values)
