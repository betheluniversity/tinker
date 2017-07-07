from testing_suite.integration_tests import BaseIntegrationTestCase


class PublishPublishTestCase(BaseIntegrationTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(PublishPublishTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = ""

    #######################
    ### Testing methods ###
    #######################

    def test_publish_publish(self):
        destination = "staging"  # or "production"
        publish_type = "page"
        publish_id = "a7404faa8c58651375fc4ed23d7468d5"
        self.request = self.generate_url("publish_publish", destination=destination, type=publish_type, id=publish_id)
        response = self.send_get(self.request)
        short_string = self.get_unique_short_string(response.data)
        publishing = self.get_unique_short_string(b'Publishing. . .')
        already_exists = self.get_unique_short_string(b'This asset already exists in the publish queue')
        expected_response = publishing + " or " + already_exists
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertTrue(publishing == short_string or already_exists == short_string, msg=failure_message)
