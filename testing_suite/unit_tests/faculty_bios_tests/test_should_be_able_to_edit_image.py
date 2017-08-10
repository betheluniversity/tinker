from flask import session

from faculty_bios_controller_base import FacultyBiosControllerBaseTestCase
from tinker import app


class ShouldBeAbleToEditImageTestCase(FacultyBiosControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ShouldBeAbleToEditImageTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_should_be_able_to_edit_image(self):
        with app.test_request_context():
            session['roles'] = ['FACULTY-CAPS']
            session['groups'] = 'Tinker Faculty Bios'
            response = self.controller.should_be_able_to_edit_image()
            self.assertTrue(isinstance(response, bool))
            self.assertTrue(response)
