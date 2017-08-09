from publish_controller_base import PublishControllerBaseTestCase


class SearchDataDefintionsTestCase(PublishControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SearchDataDefintionsTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_convert_meta_date_valid(self):
        # TODO: It appears that this method isn't tested in Integration Tests, so I'm not sure if the method
        # tinker/publish/__init__.py:publish_program_feeds_return is supposed to be tested, and that's the only place
        # that this method gets called.
        pass
