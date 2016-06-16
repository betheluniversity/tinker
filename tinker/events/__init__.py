__author__ = 'ejc84332'

from tinker import tools
from flask.ext.classy import FlaskView
from tinker.events.Events_Controller import EventsController
from flask import Blueprint, redirect
from tinker.events.cascade_events import *


EventsBlueprint = Blueprint('events', __name__, template_folder='templates')

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

    def add(self):

        # import this here so we dont load all the content
        # from cascade during hoempage load
        from tinker.events.forms import EventForm

        form = EventForm()
        add_form = True
        return render_template('event-form.html', **locals())\

    # @route('/duplicate/<event_id>')
    def duplicate_event_page(self, event_id):

        # import this here so we dont load all the content
        # from cascade during homepage load
        from tinker.events.forms import EventForm

        event_data, form_data, s_data, metadata, dynamic_fields = self.base.read_page(event_id)

        # # Get the event data from cascade
        # event_data = read(event_id)
        #
        # # Get the different data sets from the response
        # form_data = event_data.asset.page
        # # the stuff from the data def
        # s_data = form_data.structuredData.structuredDataNodes.structuredDataNode
        # # regular metadata
        # metadata = form_data.metadata
        # # dynamic metadata
        # dynamic_fields = metadata.dynamicFields.dynamicField
        # This dict will populate our EventForm object
        edit_data = {}
        date_count = 0
        dates = {}
        # Start with structuredDataNodes (data def content)
        self.base.node(s_data, edit_data, date_count, dates)

        # for node in s_data:
        #     node_identifier = node.identifier.replace('-', '_')
        #     node_type = node.type
        #     if node_type == "text":
        #         edit_data[node_identifier] = node.text
        #     elif node_type == 'group':
        #         # These are the event dates. Create a dict so we can convert to JSON later.
        #         dates[date_count] = read_date_data_structure(node)
        #         date_count += 1
        #     elif node_identifier == 'image':
        #         edit_data['image'] = node.filePath

        # now metadata dynamic fields
        self.base.metadata(dynamic_fields, edit_data)
        # for field in dynamic_fields:
        #     # This will fail if no metadata is set. It should be required but just in case
        #     if field.fieldValues:
        #         items = [item.value for item in field.fieldValues.fieldValue]
        #         edit_data[field.name.replace('-', '_')] = items

        # Add the rest of the fields. Can't loop over these kinds of metadata
        edit_data['title'] = metadata.title
        edit_data['teaser'] = metadata.metaDescription
        author = metadata.author

        # Create an EventForm object with our data
        form = EventForm(**edit_data)
        form.event_id = event_id

        # convert dates to json so we can use Javascript to create custom DateTime fields on the form
        dates = fjson.dumps(dates)
        add_form = True

        return render_template('event-form.html', **locals())

EventsView.register(EventsBlueprint)
