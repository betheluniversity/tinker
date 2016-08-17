from redirects_base import RedirectsBaseTestCase


class IndexTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /admin/redirect" didn\'t return the HTML code expected by ' + class_name + '.'
        response = super(IndexTestCase, self).send_get("/admin/redirect")
        self.assertIn(b'<form action="" id="new-redirect-form">', response.data, msg=failure_message)