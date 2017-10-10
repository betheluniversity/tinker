import datetime

from redirects_controller_base import RedirectsControllerBaseTestCase


class ExpireOldRedirectsTestCase(RedirectsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ExpireOldRedirectsTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_expire_old_redirects(self):
        # 1. Add a redirect that is ready to be expired
        from_path = '/from?'
        to_url = 'to!'
        should_have_short_url = False
        expiration_date = datetime.datetime(2016, 7, 1, 0, 0)
        expired_row = self.controller.add_row_to_db(from_path, to_url, should_have_short_url, expiration_date)

        # 2. Get a count of how many redirects are in the DB
        query_results = self.controller.get_all_rows()
        first_count = len(query_results)

        # 3. Call the expire method, which deletes redirects that have expired
        self.controller.expire_old_redirects()

        # 4. Get a new count of how many redirects are in the DB
        query_results = self.controller.get_all_rows()
        second_count = len(query_results)

        # 5. Assert that the second count is fewer than the first count
        self.assertTrue(first_count > second_count)

        # 6. Assert that the added row is no longer in the DB since the expire method should have deleted it
        query_results = self.controller.search_db('from_path', from_path)
        self.assertTrue(expired_row not in query_results)
