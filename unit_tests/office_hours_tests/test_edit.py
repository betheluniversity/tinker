from office_hours_base import OfficeHoursBaseTestCase


class EditTestCase(OfficeHoursBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(EditTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_edit(self):
        block_id = "4f78feca8c58651305d79299fb5aa2bb"
        failure_message = '"GET /office-hours/edit/%s" didn\'t return the HTML code expected by ' % block_id + self.class_name + '.'
        expected_response = b'<form id="officehoursform" action="/office-hours/" method="post" enctype="multipart/form-data">'
        response = super(EditTestCase, self).send_get("/office-hours/edit/" + block_id)
        self.assertIn(expected_response, response.data, msg=failure_message)