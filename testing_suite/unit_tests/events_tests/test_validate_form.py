from flask import session
from werkzeug.datastructures import ImmutableMultiDict

from events_controller_base import EventsControllerBaseTestCase
from tinker import app


class ValidateFormTestCase(EventsControllerBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(ValidateFormTestCase, self).__init__(methodName)

    #######################
    ### Testing methods ###
    #######################

    # todo: change the on_campus_location to pull a value from the current possible locations
    def test_validate_form_valid(self):
        test_form = {
            'end1': u'August 5th 2018, 12:00 am',
            'on_campus_location': u'Benson Great Hall',
            'wufoo_code': u'',
            'main_content': u"This is an event created to make sure that Tinker's connection with Cascade via "
                            u"events continues working as we make changes",
            'image': u'',
            'cas_departments': u'English',
            'off_campus_location': u'',
            'general': u'Athletics',
            'cost': u'$20',
            'questions': u"Why are you still reading this event? It's just a test!",
            'registration_details': u'Pay all the money.',
            'title': u'Test event',
            'event_id': u'',
            'metaDescription': u'This is an event created via unit testing',
            'start1': u'August 3rd 2018, 12:00 am',
            'internal': u'None',
            'location': u'On Campus',
            'featuring': u'Testing things!',
            'ticketing_url': u'',
            'other_on_campus': u'No.',
            'timezone1': u'',
            'sponsors': u'Eric Jameson',
            'adult_undergrad_program': u'None',
            'link': u'',
            'registration_heading': u'Registration',
            'num_dates': u'1',
            'maps_directions': u"Don't drive; take a plane.",
            'author': u'',
            'cancellations': u'Full refund',
            'offices': u'Parents',
            'graduate_program': u'None',
            'seminary_program': u'None'
        }
        with app.test_request_context(method='POST'):
            session['groups'] = ['Event Approver']
            # validate_form takes a second argument, dates_good. That's calculated in a separate method, and AND'd with
            # the results of validate. By passing in True as dates_good, it logically pares the result down to just
            # validate's return.
            response = self.controller.validate_form(ImmutableMultiDict(test_form), True)
            self.assertTrue(isinstance(response, tuple))
            self.assertEqual(len(response), 2)
            self.assertEqual(response[0].errors, {})
            self.assertTrue(isinstance(response[1], bool))
            self.assertTrue(response[1])
