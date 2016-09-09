from unit_tests import BaseTestCase


class EditTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(EditTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "GET"
        self.request = ""

    #######################
    ### Testing methods ###
    #######################

    def test_edit(self):
        block_id = "4f78feca8c58651305d79299fb5aa2bb"
        self.request = self.generate_url("edit", block_id=block_id)
        expected_response = b'<form id="officehoursform" action="/office-hours/submit" method="post" enctype="multipart/form-data">'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)