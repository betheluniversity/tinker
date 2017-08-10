from flask import session

from events_controller_base import EventsControllerBaseTestCase
from tinker import app


class SplitUserEventsTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SplitUserEventsTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_split_user_events(self):
        test_list_of_events = [
            {
                'author': 'phg49389'
            },
            {
                'author': 'phg49389'
            },
            {
                'author': 'phg49389'
            },
            {
                'author': 'enttes'
            },
            {
                'author': 'enttes'
            },
            {
                'author': None
            }
        ]
        with app.test_request_context():
            session['username'] = 'phg49389'
            response = self.controller.split_user_events(test_list_of_events)
            self.assertTrue(isinstance(response, tuple))
            self.assertEqual(len(response), 2)
            self.assertTrue(isinstance(response[0], list))
            self.assertEqual(len(response[0]), 3)
            for event in response[0]:
                self.assertTrue(isinstance(event, dict))
                self.assertTrue('author' in event.keys())
                self.assertEqual(event['author'], 'phg49389')
            self.assertTrue(isinstance(response[1], list))
            self.assertEqual(len(response[1]), 3)
            for event in response[1]:
                self.assertTrue(isinstance(event, dict))
                self.assertTrue('author' in event.keys())
                self.assertNotEqual(event['author'], 'phg49389')
