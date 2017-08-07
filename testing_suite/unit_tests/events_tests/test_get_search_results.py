from datetime import datetime

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
        selection = [u'1']
        title = ''
        start = datetime(year=2017, month=8, day=7)
        end = 0
        with app.test_request_context():
            session['username'] = 'bwj69724'
            session['groups'] = 'Administrators;Event Approver'
            session['roles'] = [u'ALUMNI-CAS', u'ALUMNI', u'STAFF', u'CAMPUS-STP', u'STAFF-STP']
            response = self.controller.get_search_results(selection, title, start, end)
            self.assertTrue(isinstance(response, tuple))
            self.assertEqual(len(response), 2)
            self.assertTrue(isinstance(response[0], list))
            self.assertTrue(len(response[0]) > 0)
            expected_keys = ['event-dates', 'is_all_day', 'html', 'author', 'path', 'title', 'created-on', 'id', 'is_published']
            for event in response[0]:
                self.assertTrue(isinstance(event, dict))
                for key in event.keys():
                    self.assertTrue(key in expected_keys)
            self.assertTrue(isinstance(response[1], str))
            self.assertEqual(response[1], 'All Events')
