import os

from program_search_controller_base import ProgramSearchControllerBaseTestCase


class CreateNewCSVFileTestCase(ProgramSearchControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CreateNewCSVFileTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_create_new_csv_file(self):
        response = self.controller.create_new_csv_file()
        self.assertIn("<pre>", response)
        self.assertIn("</pre>", response)
        self.assertTrue(os.path.isfile('./programs.csv'))
        os.remove('./programs.csv')
        self.assertFalse(os.path.isfile('./programs.csv'))
