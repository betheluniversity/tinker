import datetime

from flask import session

from redirects_controller_base import RedirectsControllerBaseTestCase
from tinker import app
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
        # Commented out to delete the old one, to make it synced again
        from_path = '/from?'
        to_url = 'to!'
        should_have_short_url = False
        expiration_date = datetime.datetime(2016, 7, 1, 0, 0)
        with app.test_request_context():
            session['username'] = 'test'
            response = self.controller.add_row_to_db(from_path, to_url, should_have_short_url, expiration_date)
            self.assertTrue(isinstance(response, BethelRedirect))
            self.assertEqual(str(response), '<Redirect %(0)s to %(1)s>' % {'0': from_path, '1': to_url})
            query_results = self.controller.search_db(from_path, to_url)
            self.assertTrue(isinstance(query_results, list))
            self.assertEqual(len(query_results), 1)
            self.assertEqual(response, query_results[0])
            self.controller.delete_row_from_db(response.id)
