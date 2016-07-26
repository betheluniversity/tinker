from . import OfficeHoursBaseTestCase


class IndexTestCase(OfficeHoursBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = self.send_get("/office-hours")
        assert b'<div class="row">\
          <div class="large-12 columns">\
            <p>Below is the list of Office Hours you have access to edit.\
            </p>\
          </div>\
         </div>\
        <hr/>\
        \
        <div class="row">\
        \
          <div class="large-12 columns">' in response.data