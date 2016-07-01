from faculty_bio_base import FacultyBioBaseTestCase


class EditTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    # Until we can get the faculty bio  and CSRF tokens returned by creation of a page over from that test to this
    # test, this will have to be tested in test_sequentially.py.
    # def test_edit(self):
    #     response = self.send_get("/faculty-bio/edit/??????????")
    #     assert b'<form id="facultybioform" action="/faculty-bio/submit" method="post" enctype="multipart/form-data">'\
    #            in response.data
    pass
