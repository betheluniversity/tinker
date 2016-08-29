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
        response = super(CompileTestCase, self).send_get("/admin/redirect/compile")
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)
