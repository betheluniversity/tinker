from redirects_base import RedirectsBaseTestCase


class IndexTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /admin/redirect"

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        expected_response = b'<form action="" id="new-redirect-form">'
        response = self.send_get("/admin/redirect")
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)