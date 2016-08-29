from redirects_base import RedirectsBaseTestCase


class IndexTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        failure_message = '"GET /admin/redirect" didn\'t return the HTML code expected by ' + self.class_name + '.'
        expected_response = b'<form action="" id="new-redirect-form">'
        response = super(IndexTestCase, self).send_get("/admin/redirect")
        self.assertIn(expected_response, response.data, msg=failure_message)