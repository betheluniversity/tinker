from faculty_bio_base import FacultyBioBaseTestCase


class DeletePageTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    # Until we can get the faculty bio  and CSRF tokens returned by creation of a page over from that test to this
    # test, this will have to be tested in test_sequentially.py.
    # def test_delete_page(self):
    #     response = self.send_get("/faculty-bio/delete/??????????????????")
    #     assert b"what?" in response.data
    pass
