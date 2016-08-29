from faculty_bio_base import FacultyBioBaseTestCase


class IndexTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        failure_message = '"GET /faculty-bio" didn\'t return the HTML code expected by ' + self.class_name + '.'
        expected_response = b"Below is a list of faculty bios you have access to edit. If you don't see your faculty"
        response = super(IndexTestCase, self).send_get("/faculty-bio")
        self.assertIn(expected_response, response.data, msg=failure_message)
