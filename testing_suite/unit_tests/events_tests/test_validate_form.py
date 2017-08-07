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

    def test_validate_form_valid(self):
        test_form = {
            'end1': u'August 5th 2017, 12:00 am',
            'on_campus_location': u'Clauson Center (CC)',
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
            'start1': u'August 3rd 2017, 12:00 am',
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
        # TODO: this validates using EventForm, which calls on session['groups'], throwing a RuntimeError
        # with app.app_context():
        #  # validate_form takes a second argument, dates_good. That's calculated in a separate method, and AND'd with
        #     # the results of validate. By passing in True as dates_good, it logically pares the result down to just
        #     # validate's return.
        #     response = self.controller.validate_form(ImmutableMultiDict(test_form), True)
        #     print response
