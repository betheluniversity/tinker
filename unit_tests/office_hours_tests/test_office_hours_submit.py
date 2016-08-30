from office_hours_base import OfficeHoursBaseTestCase


class SubmitTestCase(OfficeHoursBaseTestCase):
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
        expected_response = b'<p>Below is the list of Office Hours you have access to edit.'
        form_contents = self.create_form()
        response = super(SubmitTestCase, self).send_post("/office-hours/submit", form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        # Because this redirects to index, it uses the same assertion
        self.assertIn(expected_response, response.data, msg=failure_message)
