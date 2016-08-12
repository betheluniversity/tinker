from office_hours_base import OfficeHoursBaseTestCase


class EditTestCase(OfficeHoursBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_edit(self):
        block_id = "4f78feca8c58651305d79299fb5aa2bb"
        response = super(EditTestCase, self).send_get("/office-hours/edit/" + block_id)
        print "Edit:", response
        assert b'<form id="officehoursform" action="/office-hours/" method="post" enctype="multipart/form-data">' in response.data