from . import RedirectsBaseTestCase


class IndexTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        response = self.send_get("/admin/redirect")
        assert b'<form action="" id="new-redirect-form">\
            <div class="row">\
                <div class="large-6 columns">\
                    <label>From Path\
                        <input type="text" name="new-redirect-from" id="new-redirect-from"/>\
                    </label>\
                </div>\
                <div class="large-6 columns">\
                    <label>To URL\
                        <input type="text" name="new-redirect-to" id="new-redirect-to" />\
                    </label>\
                </div>\
            </div>\
            <div class="row">\
                <div class="large-6 columns">\
                    <label> Expiration Date.\
                        <input type="text" name="expiration-date" id="expiration-date" class="datepicker">\
                    </label>\
                </div>\
                <div class="large-6 columns">\
                    <label> Short URL\
                        <input type="checkbox" name="short-url" id="short-url" />\
                    </label>\
                </div>\
            </div>\
            <div class="row">\
                <div class="large-12 columns" id="form-save-button"></div>\
            </div>\
            </form>\
            \
            <div class="row">\
                <div class="large-12 columns">\
                    <table >\
                        <thead>\
                            <tr>\
                                <th width="400">From Path</th>\
                                <th width="400">To URL</th>\
                                <th width="400">Expiration Date</th>\
                            </tr>\
                        </thead>\
                        <tbody id="redirects-table">\
                        </tbody>\
                    </table>\
                </div>\
            </div>' in response.data