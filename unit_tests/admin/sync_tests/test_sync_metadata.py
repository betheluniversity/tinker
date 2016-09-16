from unit_tests import BaseTestCase


class MetadataTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(MetadataTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "POST"
        self.request = self.generate_url("metadata")

    def create_form(self, id):
        return {
            'id': id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_metadata_valid(self):
        expected_response = b'<h3>Successfully Synced'
        form_contents = self.create_form("yes")
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)

    def test_metadata_invalid_id(self):
        expected_response = self.ERROR_400
        form_contents = self.create_form(None)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)