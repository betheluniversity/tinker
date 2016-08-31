from office_hours_base import OfficeHoursBaseTestCase


class PostTestCase(OfficeHoursBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(PostTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

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

    def test_post(self):
        failure_message = 'Sending a valid submission to "POST /office-hours" didn\'t succeed as expected by ' + self.class_name + '.'
        expected_response = b'<p>Below is the list of Office Hours you have access to edit.'
        form_contents = self.create_form()
        response = super(PostTestCase, self).send_post("/office-hours", form_contents)
        # Because this redirects to index, it uses the same assertion
        self.assertIn(expected_response, response.data, msg=failure_message)