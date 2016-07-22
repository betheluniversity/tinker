from faculty_bio_base import FacultyBioBaseTestCase


class ConfirmEditTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_confirm_edit(self):
        response = self.send_get("/faculty-bio/confirm-edit")
        assert b"You've successfully edited your bio. Your edits have been sent for approval but will be ready to " \
               b"view in 2-3 business days. Thanks for keeping your bio up to date!" in response.data
