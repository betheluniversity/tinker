from tinker import cascade_connector
from unit_tests import BaseTestCase


class FacultyBioSequentialTestCase(BaseTestCase):
    def __init__(self, methodName):
        super(FacultyBioSequentialTestCase, self).__init__(methodName)
        self.request_type = ""
        self.request = ""

    def test_this_folder(self):
        folder_id = "018f28a88c5865136fb8da53a539394d"
        folder = cascade_connector.read(folder_id, "folder")['asset']['folder']['children']['child']
        for child in folder:
            possible_bio = cascade_connector.read(child['id'], child['type'])
            try:
                if possible_bio['asset']['page']['contentTypePath'] == "Academics/Faculty Bio":
                    fac_bio_id = possible_bio['asset']['page']['id']
                    request_url = self.generate_url("edit", faculty_bio_id=fac_bio_id)
                    response = self.send_get(request_url)
                    returned_html = response.data
                    form_data = self.get_form_data_from_html(returned_html)
                    request_url = self.generate_url("submit")
                    response = self.send_post(request_url, form_data)

                    # This method will never work; the POST request requires fields that are added in the JS submit, not
                    # in the HTML code that can be scraped.

                    # self.assertIn("String to make sure is in the code", returned_html)
            except KeyError:
                continue
