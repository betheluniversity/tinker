from faculty_bio_base import FacultyBioBaseTestCase


class IndexTestCase(FacultyBioBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    #######################
    ### Testing methods ###
    #######################

    def test_index(self):
        class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        failure_message = '"GET /faculty-bio" didn\'t return the HTML code expected by ' + class_name + '.'
        response = super(IndexTestCase, self).send_get("/faculty-bio")
        self.assertIn(b"Below is a list of faculty bios you have access to edit. If you don't see your faculty bio, please contact your web author.",
                      response.data, msg=failure_message)
