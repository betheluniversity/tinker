from office_hours_base import OfficeHoursBaseTestCase


class IndexTestCase(OfficeHoursBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = super(IndexTestCase, self).send_get("/office-hours")
        assert b'<p>Below is the list of Office Hours you have access to edit.' in response.data