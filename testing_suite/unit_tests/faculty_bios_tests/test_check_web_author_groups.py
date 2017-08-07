from faculty_bios_controller_base import FacultyBiosControllerBaseTestCase
from testing_suite.utilities import FauxElement


class CheckWebAuthorGroupsTestCase(FacultyBiosControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CheckWebAuthorGroupsTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_check_web_author_groups(self):
        test_groups = 'Math CS;Physics'
        test_program_elements = [
            [
                FauxElement('program', text='Math & Computer Science'),
                FauxElement('program', text='Physics & Engineering'),
            ]
        ]
        response = self.controller.check_web_author_groups(test_groups, test_program_elements)
        self.assertTrue(isinstance(response, bool))
        self.assertTrue(response)
