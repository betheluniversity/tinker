from . import FacultyBioBaseTestCase


class DeleteConfirmTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_delete_confirm(self):
        response = self.send_get("/faculty-bio/delete-confirm")
        assert b'Your faculty bio has been deleted. It will be removed from your <a href="https://tinker.bethel.edu">' \
               b'Tinker homepage</a> in a few minutes.' in response.data
