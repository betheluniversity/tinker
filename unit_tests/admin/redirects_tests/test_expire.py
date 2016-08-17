from redirects_base import RedirectsBaseTestCase


class ExpireTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_expire(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /admin/redirect/expire" didn\'t return "done" as expected by ' + class_name + '.'
        response = super(ExpireTestCase, self).send_get('/admin/redirect/expire')
        self.assertIn(b'done', response.data, msg=failure_message)
