from testing_suite import BaseTestCase


class SubmitTestCase(BaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SubmitTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("submit")

    def create_form(self, block_id="4f78feca8c58651305d79299fb5aa2bb"):
        # This form is essentially a "blank" edit. The update methods should see that there's no changes being made, and
        # therefore make no changes.
        return {
            "block_id": block_id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        # expected_response = b"You've successfully updated your office's hours. You should see these changes reflected"
        # form = self.create_form()
        # response = self.send_post(self.request, form)
        # failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
        #                                                 expected_response, self.class_name, self.get_line_number())
        # self.assertIn(expected_response, response.data, msg=failure_message)
        pass

    def test_submit_invalid_block_id(self):
        # expected_response = b"You've successfully updated your office's hours. You should see these changes reflected"
        # arg_names = ['block_id']
        # for i in range(len(arg_names)):
        #     bad_arg = {arg_names[i]: None}
        #     form = self.create_form(**bad_arg)
        #     response = self.send_post(self.request, form)
        #     failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
        #                                                     expected_response,
        #                                                     self.class_name + "/submit_invalid_" + arg_names[i],
        #                                                     self.get_line_number())
        #     self.assertIn(expected_response, response.data, msg=failure_message)
        pass
