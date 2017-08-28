from e_annz_controller_base import EAnnouncementsControllerBaseTestCase
from testing_suite.utilities import FauxElement


class IterateChildXMLTestCase(EAnnouncementsControllerBaseTestCase):
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
            'system-data-structure/first-date': '11-21-2017',
            'system-data-structure/second-date': '11-22-2017',
            './/dynamic-metadata': {
                'value': 'intrinsic'
            },
            'workflow': {
                'status': 'AWOL'
            },
            'system-data-structure': {
                'message': {
                    'a': 'Hello frands!'
                }
            },
            'title': 'Lord Esquire',
            'created-on': 'hope that this works'
        })
        child.attrib['id'] = '24601'
        child.find('system-data-structure').find('message').find('a').attrib['href'] = 'http://www.google.com'
        response = self.controller._iterate_child_xml(child, author='Jean Valjean')

        self.assertTrue(isinstance(response, dict))
        expected_keys = ['id', 'author', 'roles', 'created-on', 'title', 'message', 'first_date',
                         'first_date_past', 'second_date', 'second_date_past', 'workflow_status']
        for key in expected_keys:
            self.assertTrue(key in response.keys())

        self.assertTrue(isinstance(response['id'], str))
        self.assertEqual(response['id'], '24601')

        self.assertTrue(isinstance(response['author'], str))
        self.assertEqual(response['author'], 'Jean Valjean')

        self.assertTrue(isinstance(response['roles'], list))
        self.assertEqual(len(response['roles']), 1)
        self.assertEqual(response['roles'][0], 'intrinsic')

        self.assertTrue(isinstance(response['created-on'], str))
        self.assertEqual(response['created-on'], 'hope that this works')

        self.assertTrue(isinstance(response['title'], str))
        self.assertEqual(response['title'], 'Lord Esquire')

        self.assertTrue(isinstance(response['message'], str))
        self.assertEqual(response['message'], '<a href="http://www.google.com">Hello frands!</a>')

        self.assertTrue(isinstance(response['first_date'], str))
        self.assertEqual(response['first_date'], 'Tuesday November 21, 2017')

        self.assertTrue(isinstance(response['first_date_past'], bool))
        self.assertFalse(response['first_date_past'])

        self.assertTrue(isinstance(response['second_date'], str))
        self.assertEqual(response['second_date'], 'Wednesday November 22, 2017')

        self.assertTrue(isinstance(response['second_date_past'], bool))
        self.assertFalse(response['second_date_past'])

        self.assertTrue(isinstance(response['workflow_status'], str))
        self.assertEqual(response['workflow_status'], 'AWOL')
