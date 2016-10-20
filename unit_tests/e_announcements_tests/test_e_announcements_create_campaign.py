from unit_tests import BaseTestCase


class CreateCampaignTestCase(BaseTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CreateCampaignTestCase, self).__init__(methodName)
        self.request_type = "GET"
        self.request = self.generate_url("create_campaign")

    #######################
    ### Testing methods ###
    #######################

    def test_create_campaign(self):
        expected_response = b'401 UNAUTHORIZED'
        response = self.send_get(self.request)
        # Per Eric, for now we're leaving this endpoint untested. This is because this endpoint will create a Carlyle
        # campaign, but wouldn't be able to send it, so it would just pile up a bunch of unused campaigns.
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, str(response), msg=failure_message)
