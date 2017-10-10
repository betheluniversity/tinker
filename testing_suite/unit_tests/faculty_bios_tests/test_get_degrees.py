from faculty_bios_controller_base import FacultyBiosControllerBaseTestCase


class GetDegreesTestCase(FacultyBiosControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetDegreesTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_degrees(self):
        test_add_data = {
            'school1': 'a',
            'degree-earned1': 'b',
            'year1': 'c',
            'school2': 'd',
            'degree-earned2': 'e',
            'year2': 'f',
            'school3': 'g',
            'degree-earned3': 'h',
            'year3': 'i',
        }
        response = self.controller.get_degrees(test_add_data)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), 3)
        for degree in response:
            self.assertTrue(isinstance(degree, dict))
            self.assertTrue('school' in degree.keys())
            self.assertTrue('degree-earned' in degree.keys())
            self.assertTrue('year' in degree.keys())
