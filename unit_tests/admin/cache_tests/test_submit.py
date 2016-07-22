from . import ClearCacheBaseTestCase


class SubmitTestCase(ClearCacheBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        # Right now this test finishes just fine, but the method it tests is throwing an error. In tinker/tools.py, the
        # method clear_image_cache(image_path) is calling the commandline command "rm" on folders that aren't there.
        # As far as I can tell, this is because the method is written to work on the production server and references
        # files and folders in there, not on my local machine.
        form_contents = {'url': "yes"}
        response = super(SubmitTestCase, self).send_post('/admin/cache-clear/submit', form_contents)
        assert b'[' in response.data

    def test_submit_invalid_url(self):
        form_contents = {'url': None}
        response = super(SubmitTestCase, self).send_post('/admin/cache-clear/submit', form_contents)
        assert b'400 Bad Request' in response.data