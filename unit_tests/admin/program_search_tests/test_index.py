from program_search_base import ProgramSearchBaseTestCase


class IndexTestCase(ProgramSearchBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = super(IndexTestCase, self).send_get("/admin/program-search")
        assert b'<label for="key">Concentration Code or Program Name:</label>' in response.data
