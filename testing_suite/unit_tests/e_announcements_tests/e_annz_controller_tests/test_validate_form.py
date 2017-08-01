from werkzeug.datastructures import ImmutableMultiDict
from e_annz_controller_base import EAnnouncementsControllerBaseTestCase
from tinker import app


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
        # with app.app_context():
        #     response = self.controller.validate_form(ImmutableMultiDict(test_dict))
        #     print response
        # TODO: it looks like this is trying to generate CSRF token. Need to look into turning CSRF off for these tests.
