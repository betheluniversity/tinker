from cache_base import ClearCacheBaseTestCase


class SubmitTestCase(ClearCacheBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form(self, url):
        csrf_token = super(SubmitTestCase, self).get_csrf_token('/admin/cache-clear')
        return {
            'url': url,
            'csrf_token': csrf_token
        }

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        # Right now this test finishes just fine, but the method it tests is throwing an error. In tinker/tools.py, the
        # method clear_image_cache(image_path) is calling the commandline command "rm" on folders that aren't there.
        # As far as I can tell, this is because the method is written to work on the production server and references
        # files and folders in there, not on my local machine.
        form_contents = self.create_form("/yes")
        response = super(SubmitTestCase, self).send_post('/admin/cache-clear/submit', form_contents)
        assert b'Cleared:' in response.data

    def test_submit_invalid_url(self):
        form_contents = self.create_form(None)
        response = super(SubmitTestCase, self).send_post('/admin/cache-clear/submit', form_contents)
        assert b'<p>The browser (or proxy) sent a request that this server could not understand.</p>' in response.data