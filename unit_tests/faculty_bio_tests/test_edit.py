from faculty_bio_base import FacultyBioBaseTestCase


class EditTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_edit(self):
        response = self.send_get("/faculty-bio/edit")
        assert b'<form id="facultybioform" action="/faculty-bio/submit" method="post" enctype="multipart/form-data">'\
               in response.data
