from redirects_base import RedirectsBaseTestCase


class CompileTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_compile(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /admin/redirect/compile" didn\'t return "done" as expected by ' + class_name + '.'
        response = super(CompileTestCase, self).send_get("/admin/redirect/compile")
        self.assertIn(b'done', response.data, msg=failure_message)
