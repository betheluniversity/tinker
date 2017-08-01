from faculty_bios_controller_base import FacultyBiosControllerBaseTestCase


class GetWYSIWYGCheckboxesTestCase(FacultyBiosControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetWYSIWYGCheckboxesTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_wysiwyg_checkboxes(self):
        test_add_data = {
            'biography': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Biography')

        test_add_data = {
            'awards': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Awards')

        test_add_data = {
            'courses': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Courses Taught::CONTENT-XML-CHECKBOX::Professional Organizations, Committees, and Boards')

        test_add_data = {
            'publications': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Publications')

        test_add_data = {
            'presentations': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Presentations')

        test_add_data = {
            'certificates': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Certificates and Licenses')

        test_add_data = {
            'courses': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Courses Taught::CONTENT-XML-CHECKBOX::Professional Organizations, Committees, and Boards')

        test_add_data = {
            'hobbies': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Hobbies and Interests')

        test_add_data = {
            'areas': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Areas of expertise')

        test_add_data = {
            'research_interests': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Research interests')

        test_add_data = {
            'teaching_specialty': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Teaching specialty')

        test_add_data = {
            'quote': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Quote')

        test_add_data = {
            'website': 'a'
        }
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '::CONTENT-XML-CHECKBOX::Website')

        test_add_data = {}
        response = self.controller.get_wysiwyg_checkboxes(test_add_data)
        self.assertTrue(isinstance(response, str))
        self.assertEqual(response, '')
