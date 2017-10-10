from flask import session

from faculty_bios_controller_base import FacultyBiosControllerBaseTestCase
from tinker import app


class IsUserInWebAuthorGroupsTestCase(FacultyBiosControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IsUserInWebAuthorGroupsTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_is_user_in_web_author_groups(self):
        with app.test_request_context():
            session['groups'] = 'Math CS'
            response = self.controller.is_user_in_web_author_groups()
            self.assertTrue(isinstance(response, bool))
            self.assertTrue(response)
