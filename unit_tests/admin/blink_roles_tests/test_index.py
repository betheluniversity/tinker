from . import RolesBaseTestCase


class HomeTestCase(RolesBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_home_valid(self):
        response = self.send_get("/admin/blink-roles/home")
        assert b'Layout Owner Logins' in response.data