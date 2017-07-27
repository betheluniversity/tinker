from redirects_controller_base import RedirectsControllerBaseTestCase
from tinker.admin.redirects.models import BethelRedirect


class DeleteRowFromDBTestCase(RedirectsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(DeleteRowFromDBTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_delete_row_from_db(self):
        # First add a row and make sure that it's in the DB
        from_path = "/from?"
        to_url = "to!"
        added_row = self.controller.api_add_row(from_path, to_url)
        query_results = self.controller.search_db('from_path', from_path)
        self.assertTrue(isinstance(query_results, list))
        self.assertEqual(len(query_results), 1)
        self.assertEqual(added_row, query_results[0])

        # Then delete the added row and make sure it's not in the DB
        self.controller.delete_row_from_db(from_path)
        query_results = self.controller.search_db('from_path', from_path)
        self.assertTrue(isinstance(query_results, list))
        self.assertEqual(len(query_results), 0)
