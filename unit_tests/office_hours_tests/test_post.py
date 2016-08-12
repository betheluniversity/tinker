from office_hours_base import OfficeHoursBaseTestCase


class PostTestCase(OfficeHoursBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self):
        return {
            "block_id": "4f78feca8c58651305d79299fb5aa2bb"
        }

    #######################
    ### Testing methods ###
    #######################

    def test_post(self):
        form_contents = self.create_form()
        response = super(PostTestCase, self).send_post("/office-hours", form_contents)
        print "Post:", response
        # Because this redirects to index, it uses the same assertion
        assert b'<div class="row"><div class="large-12 columns">' in response.data
