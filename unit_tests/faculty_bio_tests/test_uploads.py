from faculty_bio_base import FacultyBioBaseTestCase


class UploadsTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_uploads(self):
        response = self.send_get("/faculty-bio/uploads/??????????")
        assert b'???????' in response.data
