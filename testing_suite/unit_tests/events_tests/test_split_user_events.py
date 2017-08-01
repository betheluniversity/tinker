from tinker import app, session
from events_controller_base import EventsControllerBaseTestCase


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
        # TODO: throws RuntimeError like a few other tests, need to come back and fix this
        # with app.app_context():
        #     response = self.controller.split_user_events(test_list_of_events)
