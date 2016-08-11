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
        assert b'<input type="text" name="key" id=\'search-key\' class=\'search-input\' placeholder="Filter Key" />' in response.data
