from testing_suite.integration_tests import BaseIntegrationTestCase


class SearchTestCase(BaseIntegrationTestCase):

    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(SearchTestCase, self).__init__(methodName)
        self.request_type = "POST"
        self.request = self.generate_url("search")

    def create_form(self, name="*projections-and-dreams*", content="*This exhibition brings*", metadata="*summary*",
                    pages="true", blocks="true", files="true", folders="true"):
        return {
            'name': name,
            'content': content,
            'metadata': metadata,
            'pages': pages,
            'blocks': blocks,
            'files': files,
            'folders': folders
        }

    #######################
    ### Testing methods ###
    #######################

    def test_search_valid(self):
        expected_response = repr('\xc1\xd1\x9d\x8e\xc1\xb0\xcf\xb1`\xbf\x0c\xc5\x1a\xec)\xc1')
        # b'<a href="https://cms.bethel.edu/entity/open.act?id=a7404faa8c58651375fc4ed23d7468d5&type=page">/events/arts/galleries/exhibits/2006/projections-and-dreams</a>'
        form = self.create_form()
        response = self.send_post(self.request, form)
        short_string = self.get_unique_short_string(response.data)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                        expected_response, self.class_name, self.get_line_number())
        self.assertIn(expected_response, short_string, msg=failure_message)

    def test_search_invalid(self):
        expected_response = self.ERROR_400
        arg_names = ['name', 'content', 'metadata', 'pages', 'blocks', 'files', 'folders']
        for i in range(len(arg_names)):
            bad_arg = {arg_names[i]: None}
            form = self.create_form(**bad_arg)
            response = self.send_post(self.request, form)
            short_string = self.get_unique_short_string(response.data)
            failure_message = self.generate_failure_message(self.request_type, self.request, response.data,
                                                            expected_response,
                                                            self.class_name + "/search_invalid_" + arg_names[i],
                                                            self.get_line_number())
            self.assertIn(expected_response, short_string, msg=failure_message)
