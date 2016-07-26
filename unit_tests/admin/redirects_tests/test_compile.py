from redirects_base import RedirectsBaseTestCase


class CompileTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_compile(self):
        response = super(CompileTestCase, self).send_get("/admin/redirect/compile")
        assert b'done' in response.data
