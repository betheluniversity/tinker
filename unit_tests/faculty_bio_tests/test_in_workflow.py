from faculty_bio_base import FacultyBioBaseTestCase


class InWorkflowTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_in_workflow(self):
        response = super(InWorkflowTestCase, self).send_get("/faculty-bio/in-workflow")
        assert b'You recently made edits to your bio and are currently pending approval. Please wait until the changes have been approved before you make additional edits. Go back to your <a href="/faculty-bio">faculty bios</a>' in response.data
