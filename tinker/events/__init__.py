__author__ = 'ejc84332'

from tinker import tools
from flask_classy import FlaskView
from tinker.events.Events_Controller import EventsController
from flask import session, render_template, Blueprint
from tinker.events.cascade_events import *
EventsBlueprint = Blueprint('Events', __name__, template_folder='templates')

class EventsView(FlaskView):
    route = '/event/'

    def __init__(self):
        self.base = EventsController

    def home(self):
        forms = get_forms_for_user(session['username'])
        if 'Event Approver' in tools.get_groups_for_user():
            event_approver_forms = get_forms_for_event_approver()
        return render_template('events-home.html', **locals())

    def delete_confirm(self):
        return render_template('events-delete-confirm.html', **locals())

    def confirm(self):
        return render_template('submit-confirm.html', **locals())


EventsView.register(EventsBlueprint)
