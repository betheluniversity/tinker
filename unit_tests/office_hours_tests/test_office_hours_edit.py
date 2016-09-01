from unit_tests import BaseTestCase


class EditTestCase(BaseTestCase):
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
        response = self.send_get("/office-hours/edit/" + block_id)
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)