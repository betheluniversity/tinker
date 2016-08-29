from faculty_bio_base import FacultyBioBaseTestCase


class IndexTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(IndexTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request = "GET /faculty-bio"

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        expected_response = b"Below is a list of faculty bios you have access to edit. If you don't see your faculty"
        response = super(IndexTestCase, self).send_get("/faculty-bio")
        failure_message = '"%(0)s" received "%(1)s" when it was expecting "%(2)s" in %(3)s.' % \
                          {'0': self.request, '1': response.data, '2': expected_response, '3': self.class_name}
        self.assertIn(expected_response, response.data, msg=failure_message)
