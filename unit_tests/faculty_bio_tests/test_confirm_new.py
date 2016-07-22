from . import FacultyBioBaseTestCase


class ConfirmNewTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_confirm_new(self):
        response = self.send_get("/faculty-bio/confirm-new")
        assert b"You've successfully created a new bio. Your brand new bio has been sent for approval but will be " \
               b"ready to view in 2-3 business days." in response.data
