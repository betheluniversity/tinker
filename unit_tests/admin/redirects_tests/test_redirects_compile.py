from redirects_base import RedirectsBaseTestCase


class CompileTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CompileTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /admin/redirect/compile"

    #######################
    ### Testing methods ###
    #######################

    def test_compile(self):
        expected_response = b'done'
        response = self.send_get("/admin/redirect/compile")
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
