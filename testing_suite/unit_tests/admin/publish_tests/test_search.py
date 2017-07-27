from copy import deepcopy

from suds import WebFault
from suds.sax.text import Text

from publish_controller_base import PublishControllerBaseTestCase


class SearchTestCase(PublishControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SearchTestCase, self).__init__(methodName)
        self.valid_args = {
            'name_search': '*projections-and-dreams*',
            'content_search': '*This exhibition brings*',
            'metadata_search': '*summary*',
            'pages_search': 'true',
            'blocks_search': 'true',
            'files_search': 'true',
            'folders_search': 'true'
        }

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        response = self.controller.search(**self.valid_args)

        # The response object should follow something similar to this architecture:
        # response = {
        #     'matches': {
        #         'match': [
        #             {
        #                 'id': 'a7404faa8c58651375fc4ed23d7468d5',
        #                 'path': {
        #                     'path': 'events/arts/galleries/exhibits/2006/projections-and-dreams',
        #                     'siteId': 'ba134ac58c586513100ee2a7cec27f4a',
        #                     'siteName': 'Public'
        #                 },
        #                 'recycled': False,
        #                 'type': 'page'
        #             }
        #         ]
        #     },
        #     'message': None,
        #     'success': 'true'
        # }

        self.assertEqual(response['success'], 'true')
        self.assertEqual(response['matches']['match'][0]['id'], 'a7404faa8c58651375fc4ed23d7468d5')
        self.assertEqual(response['matches']['match'][0]['path']['path'],
                         'events/arts/galleries/exhibits/2006/projections-and-dreams')
        self.assertEqual(response['matches']['match'][0]['type'], 'page')

    def test_search_invalid(self):
        # Having one of the three args be empty and the other two valid will still return a result set, so just setting
        # one as an empty string won't break it.
        #
        # That being said, by making the searches less specific, it's no longer guaranteed to return the above data.
        # Instead of asserting it's getting a specific data, instead make sure the data it's getting back is the correct
        # type and format
        args_that_wont_break_it = ['name_search', 'content_search', 'metadata_search']
        for arg in args_that_wont_break_it:
            invalid_args = deepcopy(self.valid_args)
            invalid_args[arg] = ''
            response = self.controller.search(**invalid_args)
            self.assertEqual(response['success'], 'true')
            self.assertTrue(isinstance(response['matches']['match'][0]['id'], Text))
            self.assertEqual(len(response['matches']['match'][0]['id']), 32)
            self.assertIn('events/', response['matches']['match'][0]['path']['path'])
            self.assertEqual(response['matches']['match'][0]['type'], 'page')

        # These will throw WebFault exceptions because they have to parse to boolean values
        args_that_will_break_it = ['pages_search', 'blocks_search', 'files_search', 'folders_search']
        for arg in args_that_will_break_it:
            invalid_args = deepcopy(self.valid_args)
            invalid_args[arg] = ''
            self.assertRaises(WebFault, self.controller.search, **invalid_args)
