from office_hours_base import OfficeHoursBaseTestCase


class EditTestCase(OfficeHoursBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(EditTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /office-hours/edit"

    #######################
    ### Testing methods ###
    #######################

    def test_edit(self):
        block_id = "4f78feca8c58651305d79299fb5aa2bb"
        expected_response = b'<form id="officehoursform" action="/office-hours/submit" method="post" enctype="multipart/form-data">'
        response = super(EditTestCase, self).send_get("/office-hours/edit/" + block_id)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)