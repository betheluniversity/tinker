from unit_tests import BaseTestCase


class PublishPublishTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(PublishPublishTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
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
        publishing = b'Publishing. . .' in response.data
        already_exists = b'This asset already exists in the publish queue' in response.data
        expected_response = "'Publishing. . .' or 'This asset already exists in the publish queue'"
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertTrue(publishing or already_exists, msg=failure_message)
