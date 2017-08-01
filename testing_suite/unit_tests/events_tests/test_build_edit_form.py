from events_controller_base import EventsControllerBaseTestCase


class BuildEditFormTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(BuildEditFormTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_build_edit_form(self):
        # This method is hard to test by itself and is already being tested by integration tests. As such, leaving it
        # without a unit test for the time being.
        # TODO
        pass
