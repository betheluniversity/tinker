from program_search_controller_base import ProgramSearchControllerBaseTestCase


class GetProgramsForDropdownTestCase(ProgramSearchControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetProgramsForDropdownTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_programs_for_dropdown(self):
        response = self.controller.get_programs_for_dropdown()
        self.assertTrue(isinstance(response, list))
        top_major = response[0]
        self.assertTrue(isinstance(top_major, dict))
        self.assertTrue('school' in top_major.keys())
        self.assertEqual(top_major['school'], 'College of Arts & Sciences')
        self.assertTrue('name' in top_major.keys())
        self.assertEqual(top_major['name'], '5 Year Ministry Dual Degree Program')
        self.assertTrue('value' in top_major.keys())
        self.assertEqual(top_major['value'], '5-year-ministry-major-program')
