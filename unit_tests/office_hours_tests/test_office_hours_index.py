from office_hours_base import OfficeHoursBaseTestCase


class IndexTestCase(OfficeHoursBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /office-hours"

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        expected_response = b'<p>Below is the list of Office Hours you have access to edit.'
        response = super(IndexTestCase, self).send_get("/office-hours")
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)