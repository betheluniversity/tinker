from faculty_bios_controller_base import FacultyBiosControllerBaseTestCase
from testing_suite.utilities import FauxElement


class IterateChildXMLTestCase(FacultyBiosControllerBaseTestCase):
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
            'workflow': {
                'status': 'stalled'
            },
            'path': '/righteous',
            './/job-titles/school': 'hard knocks',
            'author': 'thing 1',
            'title': 'cat in hat',
            'created-on': 'an invisible jet',
            './/last': 'comes before middle',
            './/deactivate': '007'

        })
        child.attrib['id'] = 'bondJamesBond'
        response = self.controller._iterate_child_xml(child, author='thing 2')

        self.assertTrue(isinstance(response, dict))
        expected_keys = ['id', 'author', 'title', 'last-name', 'schools', 'path', 'created-on', 'deactivated']
        for key in expected_keys:
            self.assertTrue(key in response.keys())

        self.assertTrue(isinstance(response['id'], str))
        self.assertEqual(response['id'], 'bondJamesBond')

        self.assertTrue(isinstance(response['author'].text, str))
        self.assertEqual(response['author'].text, 'thing 1')

        self.assertTrue(isinstance(response['title'], str))
        self.assertEqual(response['title'], 'cat in hat')

        self.assertTrue(isinstance(response['last-name'], str))
        self.assertEqual(response['last-name'], 'comes before middle')

        self.assertTrue(isinstance(response['schools'], list))
        self.assertEqual(len(response['schools']), 1)
        self.assertTrue(isinstance(response['schools'][0], str))
        self.assertEqual(response['schools'][0], 'hard knocks')

        self.assertTrue(isinstance(response['path'], str))
        self.assertEqual(response['path'], 'https://www.bethel.edu/righteous')

        self.assertTrue(isinstance(response['created-on'], str))
        self.assertEqual(response['created-on'], 'an invisible jet')

        self.assertTrue(isinstance(response['deactivated'], str))
        self.assertEqual(response['deactivated'], '007')
