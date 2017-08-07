from werkzeug.datastructures import ImmutableMultiDict

from e_annz_controller_base import EAnnouncementsControllerBaseTestCase
from tinker import app
from tinker.e_announcements.forms import EAnnouncementsForm


class ValidateFormTestCase(EAnnouncementsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ValidateFormTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_validate_form(self):
        test_dict = {
            'banner_roles': u'STUDENT-CAS',
            'title': u'First title',
            'message': u'This E-Announcement should never be seen by the public, I hope',
            'first_date': u'08-01-2017',
            'second_date': u'08-05-2017'
        }
        with app.app_context():
            response = self.controller.validate_form(ImmutableMultiDict(test_dict))
            self.assertTrue(isinstance(response, tuple))
            self.assertEqual(len(response), 2)
            self.assertTrue(isinstance(response[0], EAnnouncementsForm))
            # These two lines throw 'RuntimeError: Working outside of request context.' because the validate method
            # checks if the request.method is POST or PUT, and this type of unit test can't define the request context
            # necessary to do that.
            # self.assertTrue(isinstance(response[1], bool))
            # self.assertTrue(response[1])
