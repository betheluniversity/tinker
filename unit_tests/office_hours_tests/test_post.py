from office_hours_base import OfficeHoursBaseTestCase


class PostTestCase(OfficeHoursBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self):
        return {
            "block_id": ""
        }

    #######################
    ### Testing methods ###
    #######################

    def test_post(self):
        form_contents = self.create_form()
        response = super(PostTestCase, self).send_post("/office-hours", form_contents)
        # Because this redirects to index, it uses the same assertion
        assert b'<div class="row"><div class="large-12 columns">' in response.data
        #     <p>Below is the list of Office Hours you have access to edit.\
        #     </p>\
        #   </div>\
        #  </div>\
        # <hr/>\
        # \
        # <div class="row">\
        # \
        #   <div class="large-12 columns">' in response.data
