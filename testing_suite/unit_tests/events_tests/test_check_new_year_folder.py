from events_controller_base import EventsControllerBaseTestCase


class CheckNewYearFolderTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(CheckNewYearFolderTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    def test_check_new_year_folder(self):
        # This is kind of a void method, so I'm not sure how to test it properly.
        event_id = '0d9e86b88c586513543f13a687e61d4a'
        add_data = {
            'end1': u'August 5th 2017, 12:00 am',
            'on_campus_location': u'Clauson Center (CC)',
            'wufoo_code': u'',
            'other_on_campus': u'No.',
            'image': u'',
            'cas_departments': [u'English'],
            'off_campus_location': u'',
            'general': [u'Athletics'],
            'cost': u'$20', 'questions': "Why are you still reading this event? It's just a test!",
            'metaDescription': u'This is an event created via unit testing',
            'title': u'Edited title', 'event_id': u'65a1f5a68c586513260ac2978d6884da',
            'registration_details': 'Pay all the money.',
            'start1': u'August 3rd 2017, 12:00 am',
            'graduate_program': [u'None'],
            'internal': [u'None'],
            'location': u'On Campus',
            'featuring': u'Testing things!',
            'ticketing_url': u'',
            'main_content': "This is an event created to make sure that Tinker's connection with Cascade via events continues working as we make changes",
            'timezone1': u'',
            'sponsors': 'Eric Jameson',
            'link': None,
            'registration_heading': u'Registration',
            'num_dates': u'1',
            'maps_directions': "Don't drive; take a plane.",
            'system_name': u'edited-title',
            'name': u'edited-title',
            'author': 'phg49389',
            'cancellations': u'Full refund',
            'event-dates': [
                    {
                        'no-end-date': '',
                        'time-zone': u'',
                        'start-date': 1501736400000,
                        'outside-of-minnesota': 'No',
                        'end-date': 1501909200000,
                        'all-day': 'No'
                    }
                ],
            'offices': [u'Parents'],
            'adult_undergrad_program': [u'None'],
            'seminary_program': [u'None']
        }

        response = self.controller.check_new_year_folder(event_id, add_data, 'phg49389')
        # self.assertTrue(isinstance(response, None))
