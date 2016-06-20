from events_base import EventsBaseTestCase


class SudmitEditFormTestCase(EventsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_form_contents(self, title, general, offices, cas_departments, internal, adult_undergrad_program,
                             graduate_program, seminary_program, event_dates, author, event_id):
        return {
            "title": title,
            "genereal": general,
            "offices": offices,
            "cas_departments": cas_departments,
            "internal": internal,
            "adult_undergrad_program": adult_undergrad_program,
            "graduate_program": graduate_program,
            "seminary_program": seminary_program,
            "event-dates": event_dates,
            "author": author,
            "event_id": event_id
        }

    #######################
    ### Testing methods ###
    #######################

    def test_submit_edit_valid(self):
        # TODO: fill in the arguments to send a valid form submission as a test
        form_contents = self.create_form_contents("", "", "", "", "", "", "", "", "", "", "")
        response = self.send_post("/event/submit-edit", form_contents)
        print "Submit Edit Form:", response
        assert b' ' in response.data

    # TODO: write invalid tests by sending over None objects instead of the correct string arguments
