from redirects_controller_base import RedirectsControllerBaseTestCase


class RollbackTestCase(RedirectsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(RollbackTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_rollback(self):
        # This method shouldn't be unit tested, so this file is here as a stand-in. If rollback gets to the point where
        # we want to unit test it, then this is where that will happen.
        pass