from program_search_base import ProgramSearchBaseTestCase


class DeleteTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_delete(self):
        id = "2044"  # (athletic-, Coaching)
        response = super(DeleteTestCase, self).send_get("/admin/program-search/delete/" + id)
        assert b'done' in response.data
