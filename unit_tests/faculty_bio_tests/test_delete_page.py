from faculty_bio_base import FacultyBioBaseTestCase


class DeletePageTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_delete_page(self):
        response = self.send_get("/faculty-bio/delete/??????????????????")
        assert b"what?" in response.data
