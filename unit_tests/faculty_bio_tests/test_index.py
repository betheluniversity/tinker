from faculty_bio_base import FacultyBioBaseTestCase


class IndexTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = self.send_get("/faculty-bio")
        assert b"Below is a list of faculty bios you have access to edit. If you don't see your faculty bio, please " \
               b"contact your web author." in response.data
