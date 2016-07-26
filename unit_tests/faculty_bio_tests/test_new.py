from faculty_bio_base import FacultyBioBaseTestCase


class NewTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_new(self):
        response = super(NewTestCase, self).send_get("/faculty-bio/new")
        assert b'<form id="facultybioform" action="/faculty-bio/submit" method="post" enctype="multipart/form-data">' in response.data
