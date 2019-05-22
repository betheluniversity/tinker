from redirects_controller_base import RedirectsControllerBaseTestCase
from tinker.admin.redirects.models import BethelRedirect


class SearchDBTestCase(RedirectsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SearchDBTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_search_db_valid(self):
        from_path = '/welcome-week'
        to_url = ''
        response = self.controller.search_db(from_path, to_url)
        self.assertTrue(isinstance(response, list))
        self.assertTrue(len(response) > 0)
        first_result = response[0]
        self.assertTrue(isinstance(first_result, BethelRedirect))

    def test_search_db_invalid(self):
        # Test to make sure that passing in an invalid search type breaks the method
        invalid_args = {
            'search_type': None,
            'term': None
        }
        self.assertRaises(TypeError, self.controller.search_db, **invalid_args)
        # If a string other than 'from_path' is passed in as search_type, it'll default to the to_url search

        # Make sure that passing in a term that isn't a string breaks it
        invalid_args['search_type'] = 'from_path'
        self.assertRaises(TypeError, self.controller.search_db, **invalid_args)
