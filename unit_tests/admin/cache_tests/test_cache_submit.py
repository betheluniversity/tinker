from cache_base import ClearCacheBaseTestCase


class SubmitTestCase(ClearCacheBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SubmitTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    def create_form(self, url):
        return {
            'url': url
        }

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        failure_message = 'A valid form submission to "POST /admin/cache-clear/submit" failed when it should have ' \
                          'succeeded in ' + self.class_name + '.'
        expected_response = b'Cleared:'
        # Right now this test finishes just fine, but the method it tests is throwing an error. In tinker/tools.py, the
        # method clear_image_cache(image_path) is calling the commandline command "rm" on folders that aren't there.
        # As far as I can tell, this is because the method is written to work on the production server and references
        # files and folders in there, not on my local machine.
        form_contents = self.create_form("/yes")
        response = super(SubmitTestCase, self).send_post('/admin/cache-clear/submit', form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_submit_invalid_url(self):
        failure_message = 'An invalid form submission (invalid URL) to "POST /admin/cache-clear/submit" didn\'t fail ' \
                          'as expected in ' + self.class_name + '.'
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form(None)
        response = super(SubmitTestCase, self).send_post('/admin/cache-clear/submit', form_contents)
        self.assertIn(expected_response, response.data, msg=failure_message)
