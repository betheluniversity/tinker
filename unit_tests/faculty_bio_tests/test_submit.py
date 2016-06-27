from faculty_bio_base import FacultyBioBaseTestCase


class SubmitTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form_submission(self):
        return {}

    #######################
    ### Testing methods ###
    #######################

    def test_submit(self):
        form_contents = self.create_form_submission()
        response = self.send_post("/faculty-bio/submit", form_contents)
        assert b'???????' in response.data
