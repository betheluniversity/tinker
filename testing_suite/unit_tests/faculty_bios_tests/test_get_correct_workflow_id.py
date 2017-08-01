from tinker import app
from faculty_bios_controller_base import FacultyBiosControllerBaseTestCase


class GetCorrectWorkflowIDTestCase(FacultyBiosControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetCorrectWorkflowIDTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_correct_workflow(self):
        test_add_data = {
            'schools': 'College of Arts and Sciences'
        }
        response = self.controller.get_correct_workflow_id(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, app.config['FACULTY_BIOS_WORKFLOW_CAS_ID'])

        test_add_data = {
            'schools': 'Graduate School'
        }
        response = self.controller.get_correct_workflow_id(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, app.config['FACULTY_BIOS_WORKFLOW_CAPSGS_ID'])

        test_add_data = {
            'schools': 'College of Adult and Professional Studies'
        }
        response = self.controller.get_correct_workflow_id(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, app.config['FACULTY_BIOS_WORKFLOW_CAPSGS_ID'])

        test_add_data = {
            'schools': 'Bethel Seminary'
        }
        response = self.controller.get_correct_workflow_id(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, app.config['FACULTY_BIOS_WORKFLOW_SEM_ID'])

        test_add_data = {}
        response = self.controller.get_correct_workflow_id(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, app.config['FACULTY_BIOS_WORKFLOW_CAS_ID'])
