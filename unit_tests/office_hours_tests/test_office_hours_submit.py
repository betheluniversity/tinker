from unit_tests import BaseTestCase


class SubmitTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SubmitTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "POST /office-hours"

    def create_form(self):
        # This form is essentially a "blank" edit. The update methods should see that there's no changes being made, and
        # therefore make no changes.
        id_to_test = "4f78feca8c58651305d79299fb5aa2bb"
        return {
            "block_id": id_to_test
        }

    #######################
    ### Testing methods ###
    #######################

    def test_submit(self):
        expected_response = b"You've successfully updated your office's hours. You should see these changes reflected"
        form_contents = self.create_form()
        response = self.send_post("/office-hours/submit", form_contents)
        failure_message = self.generate_failure_message(self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
