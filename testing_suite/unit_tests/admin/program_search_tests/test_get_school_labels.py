from program_search_controller_base import ProgramSearchControllerBaseTestCase


class GetSchoolLabelsTestCase(ProgramSearchControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetSchoolLabelsTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_school_labels(self):
        response = self.controller.get_school_labels()
        self.assertTrue(isinstance(response, list))
        self.assertTrue('College of Arts & Sciences' in response)
        self.assertTrue('College of Adult & Professional Studies' in response)
        self.assertTrue('Graduate School' in response)
        self.assertTrue('Bethel Seminary' in response)
