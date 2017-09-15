from faculty_bios_controller_base import FacultyBiosControllerBaseTestCase


class GetJobTitlesTestCase(FacultyBiosControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(GetJobTitlesTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_get_job_titles(self):
        test_add_data = {
            'schools1': 'a1',
            'undergrad1': 'b1',
            'adult-undergrad1': 'c1',
            'graduate1': 'd1',
            'seminary1': 'e1',
            'dept-chair1': 'f1',
            'program-director1': 'g1',
            'lead-faculty1': 'h1',
            'new-job-title1': 'i1',
            'schools2': 'a2',
            'undergrad2': 'b2',
            'adult-undergrad2': 'c2',
            'graduate2': 'R2-D2',
            'seminary2': 'e2',
            'dept-chair2': 'f2',
            'program-director2': 'g2',
            'lead-faculty2': 'h2',
            'new-job-title2': 'i2',
            'schools3': 'a3',
            'undergrad3': 'b3',
            'adult-undergrad3': 'C-3PO',
            'graduate3': 'd3',
            'seminary3': 'e3',
            'dept-chair3': 'f3',
            'program-director3': 'g3',
            'lead-faculty3': 'h3',
            'new-job-title3': 'i3'
        }
        response = self.controller.get_job_titles(test_add_data)
        self.assertTrue(isinstance(response, list))
        self.assertEqual(len(response), 3)
        for job_title in response:
            self.assertTrue(isinstance(job_title, dict))
            self.assertTrue('school' in job_title.keys())
            self.assertTrue('department' in job_title.keys())
            self.assertTrue('adult-undergrad-program' in job_title.keys())
            self.assertTrue('graduate-program' in job_title.keys())
            self.assertTrue('seminary' in job_title.keys())
            self.assertTrue('department-chair' in job_title.keys())
            self.assertTrue('program-director' in job_title.keys())
            self.assertTrue('lead-faculty' in job_title.keys())
            self.assertTrue('job_title' in job_title.keys())
