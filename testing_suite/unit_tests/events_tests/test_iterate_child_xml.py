from datetime import datetime

from events_controller_base import EventsControllerBaseTestCase
from testing_suite.utilities import FauxElement


class IterateChildXMLTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IterateChildXMLTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_iterate_child_xml(self):
        child = FauxElement('element', children={
            'last-published-on': 'Tuesday',
            'event-dates': {
                'start-date': '1502468460000',
                'end-date': '1502488460000',
                'all-day': 'No'
            },
            'id': '7of9',
            'title': 'Tertiary Adjunct of Unimatrix 01',
            'created-on': 'Monday',
            'path': 'less-traveled',

        })
        response = self.controller._iterate_child_xml(child, author='Jeri Ryan')

        self.assertTrue(isinstance(response, dict))
        expected_keys = ['id', 'created-on', 'is_published', 'author', 'title', 'html', 'path', 'event-dates',
                         'is_all_day']
        for key in expected_keys:
            self.assertTrue(key in response.keys())

        self.assertTrue(isinstance(response['id'], str))
        self.assertEqual(response['id'], '7of9')

        self.assertTrue(isinstance(response['created-on'], str))
        self.assertEqual(response['created-on'], 'Monday')

        self.assertTrue(isinstance(response['is_published'], str))
        self.assertEqual(response['is_published'], 'Tuesday')

        self.assertTrue(isinstance(response['author'], str))
        self.assertEqual(response['author'], 'Jeri Ryan')

        self.assertTrue(isinstance(response['title'], str))
        self.assertEqual(response['title'], 'Tertiary Adjunct of Unimatrix 01')

        self.assertTrue(isinstance(response['html'], str))
        self.assertIn('August 11, 2017 |', response['html'])

        self.assertTrue(isinstance(response['path'], str))
        self.assertEqual(response['path'], 'https://www.bethel.edu/less-traveled')

        self.assertTrue(isinstance(response['event-dates'], list))
        self.assertEqual(len(response['event-dates']), 1)
        event_dates = response['event-dates'][0]
        self.assertTrue(isinstance(event_dates, dict))
        self.assertTrue('start' in event_dates.keys())
        self.assertTrue(isinstance(event_dates['start'], int))
        self.assertEqual(event_dates['start'], 1502468460)
        self.assertTrue('end' in event_dates.keys())
        self.assertTrue(isinstance(event_dates['end'], int))
        self.assertEqual(event_dates['end'], 1502488460)

        self.assertTrue(isinstance(response['is_all_day'], str))
        self.assertEqual(response['is_all_day'], 'No')
