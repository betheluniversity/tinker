from redirects_controller_base import RedirectsControllerBaseTestCase
from tinker.admin.redirects.models import BethelRedirect


class APIAddRowTestCase(RedirectsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(APIAddRowTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_api_add_row_valid(self):
        from_path = "/from?"
        to_url = "to!"
        response = self.controller.api_add_row(from_path, to_url)
        self.assertTrue(isinstance(response, BethelRedirect))
        self.assertEqual(str(response), '<Redirect %(0)s to %(1)s>' % {'0': from_path, '1': to_url})
        query_results = self.controller.search_db('from_path', from_path)
        self.assertTrue(isinstance(query_results, list))
        self.assertTrue(len(query_results) == 1)
        self.assertEqual(response, query_results[0])
        self.controller.delete_row_from_db(from_path)

    def test_api_add_row_invalid(self):
        # TODO: just like add_row, until we figure out how to catch those exceptions we can't really test this
        pass
