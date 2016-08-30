from blink_roles_base import RolesBaseTestCase


class IndexTestCase(RolesBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /admin/blink-roles"

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        expected_response = b'<form id="blink-login" action="https://blink.bethel.edu/cp/home/login" method="post">'
        response = super(IndexTestCase, self).send_get("/admin/blink-roles")
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)
