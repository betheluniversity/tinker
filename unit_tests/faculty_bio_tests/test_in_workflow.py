from . import FacultyBioBaseTestCase


class InWorkflowTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_in_workflow(self):
        response = self.send_get("/faculty-bio/in-workflow")
        assert b'You recently made edits to your bio and are currently pending approval. Please wait until the changes ' \
               b'have been approved before you make additional edits. Go back to your <a href="/faculty-bio">faculty ' \
               b'bios</a>' in response.data
