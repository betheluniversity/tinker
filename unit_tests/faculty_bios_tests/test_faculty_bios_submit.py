from unit_tests import BaseTestCase


class SubmitTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SubmitTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "POST"
        self.request = self.generate_url("submit")

    def create_form(self, block_id):
        return {
            'block_id': block_id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        expected_response = b'You've successfully updated your office's hours. You should see these changes reflected '
        form_contents = self.create_form("4f78feca8c58651305d79299fb5aa2bb")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)


    def test_submit_invalid_block_id(self):
        expected_response = b'400 Bad Request'
        form_contents = self.create_form(None)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
