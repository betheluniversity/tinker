from flask import session

from tinker import app
from events_controller_base import EventsControllerBaseTestCase


class GetSearchResultsTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetSearchResultsTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_search_results(self):
        selection = [u'2']
        title = ''
        start = '2017-07-27 00:00:00'
        end = 0
        # TODO: this is getting 'RuntimeError: Working outside of request context.'
        # with app.app_context():
        #     response = self.controller.get_search_results(selection, title, start, end)
        #     print response
