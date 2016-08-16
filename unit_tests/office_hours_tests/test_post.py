from office_hours_base import OfficeHoursBaseTestCase


class PostTestCase(OfficeHoursBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

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
        form_contents = self.create_form()
        response = super(PostTestCase, self).send_post("/office-hours", form_contents)
        # Because this redirects to index, it uses the same assertion
        assert b'<p>Below is the list of Office Hours you have access to edit.' in response.data
