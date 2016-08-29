from cache_base import ClearCacheBaseTestCase


class SubmitTestCase(ClearCacheBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SubmitTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "POST /admin/cache-clear/submit"

    def create_form(self, url):
        return {
            'url': url
        }

    #######################
    ### Testing methods ###
    #######################

    def test_submit_valid(self):
        expected_response = b'Cleared:'
        # Right now this test finishes just fine, but the method it tests is throwing an error. In tinker/tools.py, the
        # method clear_image_cache(image_path) is calling the commandline command "rm" on folders that aren't there.
        # As far as I can tell, this is because the method is written to work on the production server and references
        # files and folders in there, not on my local machine.
        form_contents = self.create_form("/yes")
        response = super(SubmitTestCase, self).send_post('/admin/cache-clear/submit', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_submit_invalid_url(self):
        expected_response = b'<p>The browser (or proxy) sent a request that this server could not understand.</p>'
        form_contents = self.create_form(None)
        response = super(SubmitTestCase, self).send_post('/admin/cache-clear/submit', form_contents)
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)
