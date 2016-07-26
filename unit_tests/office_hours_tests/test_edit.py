from . import OfficeHoursBaseTestCase


class EditTestCase(OfficeHoursBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_edit(self):
        block_id = ""
        response = self.send_get("/office-hours/edit/" + block_id)
        assert b'<form id="officehoursform" action="/office-hours/" method="post" enctype="multipart/form-data">' in response.data