__author__ = 'ejc84332'

from tinker import tools
from flask.ext.classy import FlaskView
from tinker.events.Events_Controller import EventsController
from flask import Blueprint, redirect
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

    def delete_page(self, page_id):
        # workflow = get_event_delete_workflow()
        # delete(page_id, workflow=workflow)
        self.base.delete(page_id)
        # publish_event_xml()
        self.base.publish(app.config['EVENT_XML_ID'])
        return redirect('/event/delete-confirm', code=302)

    def delete_confirm(self):
        return render_template('events-delete-confirm.html', **locals())

    def confirm(self):
        return render_template('submit-confirm.html', **locals())

    def event_in_workflow(self):
        return render_template('event-in-workflow.html')

EventsView.register(EventsBlueprint)
