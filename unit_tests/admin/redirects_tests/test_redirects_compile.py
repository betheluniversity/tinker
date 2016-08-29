from redirects_base import RedirectsBaseTestCase


class CompileTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CompileTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_compile(self):
        failure_message = '"GET /admin/redirect/compile" didn\'t return "done" as expected by ' + self.class_name + '.'
        expected_response = b'done'
        response = super(CompileTestCase, self).send_get("/admin/redirect/compile")
        self.assertIn(expected_response, response.data, msg=failure_message)
