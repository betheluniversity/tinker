from program_search_controller_base import ProgramSearchControllerBaseTestCase
from testing_suite.utilities import FauxElement


class GetProgramNameTestCase(ProgramSearchControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetProgramNameTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_program_name_valid(self):
        block = FauxElement('block', children={
            'display-name': 'foo',
            'title': 'bar',
            'dynamic-metadata': {
                'name': {
                    'value': 'fizz'
                }
            }
        })
        concentration = FauxElement('concentration', children={
            './/concentration_name': 'bin',
        })
        response = self.controller.get_program_name(block, concentration)
        self.assertEqual(response, 'bin')
