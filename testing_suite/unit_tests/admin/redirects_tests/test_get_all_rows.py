from redirects_controller_base import RedirectsControllerBaseTestCase
from tinker.admin.redirects.models import BethelRedirect


class GetAllRowsTestCase(RedirectsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetAllRowsTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_all_rows(self):
        response = self.controller.get_all_rows()
        self.assertTrue(isinstance(response, list))
        self.assertTrue(len(response) > 0)
        self.assertTrue(isinstance(response[0], BethelRedirect))
