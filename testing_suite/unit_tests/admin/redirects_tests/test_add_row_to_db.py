import datetime

from sqlalchemy.exc import IntegrityError

from redirects_controller_base import RedirectsControllerBaseTestCase
from tinker.admin.redirects.models import BethelRedirect


class AddRowToDBTestCase(RedirectsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(AddRowToDBTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_add_row_to_db_valid(self):
        from_path = '/from?'
        to_url = 'to!'
        should_have_short_url = False
        expiration_date = datetime.datetime(2016, 7, 1, 0, 0)
        response = self.controller.add_row_to_db(from_path, to_url, should_have_short_url, expiration_date)
        self.assertTrue(isinstance(response, BethelRedirect))
        self.assertEqual(str(response), '<Redirect %(0)s to %(1)s>' % {'0': from_path, '1': to_url})
        query_results = self.controller.search_db('from_path', from_path)
        self.assertTrue(isinstance(query_results, list))
        self.assertEqual(len(query_results), 1)
        self.assertEqual(response, query_results[0])
        self.controller.delete_row_from_db(from_path)

    def test_add_row_to_db_invalid(self):
        invalid_args = {
            'from_path': None,
            'to_url': "to!",
            'short_url': False,
            'expiration_date': datetime.datetime(2016, 7, 1, 0, 0)
        }
        # Because we have to rollback the DB after this exception, I can't use self.assertRaises
        integrity_error_caught = False
        try:
            self.controller.add_row_to_db(**invalid_args)
        except IntegrityError:
            integrity_error_caught = True
            self.controller.rollback()

        self.assertTrue(integrity_error_caught)
