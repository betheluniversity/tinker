import json
import time
import datetime
from flask import Response
from flask_classy import FlaskView, route
from tinker.events.events_controller import EventsController
from bu_cascade.asset_tools import update
from flask import Blueprint, redirect, session, render_template, request, url_for, json as fjson
from tinker import app
from events_metadata import metadata_list
# python 2.6 or earlier -- Todo: when we upgrade, use from collections import OrderedDict
from ordereddict import OrderedDict

EventsBlueprint = Blueprint('events', __name__, template_folder='templates')


class EventsView(FlaskView):
    route_base = '/events'

    def __init__(self):
        self.base = EventsController()
        self.base.datetime_format = "%B %d %Y, %I:%M %p"

    # Allows any user to access events
    def before_request(self, name, **kwargs):
        pass

    def index(self):
        show_create = True
        if 'Tinker Events - CAS' in session['groups'] or 'Event Approver' in session['groups']:
            # The special admin view
            all_schools = OrderedDict({
                1: 'All Events',
                2: 'My Events',
                3: 'Other Events'},
                key=lambda t: t[0]
            )
            # The below can be added inside of the dictionary as they are built out
            # {4: 'College of Arts and Sciences'},
            # {5: 'College of Adult and Professional Studies'},
            # {6: 'Graduate School'},
            # {7: 'Bethel Seminary'},
            # {8: 'Administration with Faculty Status'},
            # {9: 'Other'}
        else:  # normal view
            all_schools = OrderedDict({
                2: 'User Events'}
            )
        return render_template('events-home.html', show_create=show_create, all_schools=all_schools, list_of_events=None,
                               formsHeader="All Events")

    def confirm(self):
        return render_template('submit-confirm.html', **locals())

    def event_in_workflow(self):
        return render_template('event-in-workflow.html')

    def add(self):
        # import this here so we dont load all the content from cascade during homepage load
        from tinker.events.forms import EventForm

        form = EventForm()
        new_form = True
        return render_template('event-form.html', **locals())

    def edit(self, event_id):
        # if the event is in a workflow currently, don't allow them to edit. Instead, redirect them.
        if self.base.asset_in_workflow(event_id, asset_type='page'):
            return redirect(url_for('events.EventsView:event_in_workflow'), code=302)

        edit_data, dates, author = self.base.build_edit_form(event_id)
        # todo: fix this with the submit_all() functionality ASK CALEB
        # convert 'On/Off campus' to 'On/Off Campus' for all events
        from tinker.events.forms import EventForm
        form = EventForm(**edit_data)
        if 'location' in edit_data and edit_data['location']:
            edit_data['location'].replace(' c', ' C')

        return render_template('event-form.html', **locals())

    def duplicate(self, event_id):
        edit_data, dates, author = self.base.build_edit_form(event_id)
        from tinker.events.forms import EventForm
        form = EventForm(**edit_data)
        new_form = True

        return render_template('event-form.html', **locals())

    @route("/submit", methods=['post'])
    def submit(self):
        rform = request.form
        username = session['username']
        eid = rform.get('event_id')
        dates, dates_good, num_dates = self.base.check_event_dates(rform)
        failed = self.base.validate_form(rform, dates_good, dates)
        workflow = self.base.create_workflow(app.config['EVENTS_WORKFLOW_ID'], rform['author'] + '--' + rform['title'] + ', ' + datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p"))

        wysiwyg_keys = ['main_content', 'questions', 'link', 'registration_details', 'sponsors', 'maps_directions']
        if failed:
            return failed

        if not eid:
            bid = app.config['EVENTS_BASE_ASSET']
            event_data, metadata, structured_data = self.base.cascade_connector.load_base_asset_by_id(bid, 'page')
            add_data = self.base.get_add_data(metadata_list, rform, wysiwyg_keys)
            add_data['event-dates'] = self.base.get_dates(add_data)
            add_data['author'] = request.form['author']
            asset = self.base.get_event_structure(event_data, metadata, structured_data, add_data, username, workflow=workflow)
            resp = self.base.create_page(asset)
            eid = resp.asset['page']['id']
            self.base.log_sentry("New event submission", resp)
        else:
            page = self.base.read_page(eid)
            event_data, metadata, structured_data = page.get_asset()
            add_data = self.base.get_add_data(metadata_list, rform, wysiwyg_keys)
            add_data['event-dates'] = self.base.get_dates(add_data)
            add_data['author'] = request.form['author']
            asset = self.base.get_event_structure(event_data, metadata, structured_data, add_data, username, workflow=workflow, event_id=eid)

            self.base.check_new_year_folder(eid, add_data, username)
            proxy_page = self.base.read_page(eid)
            resp = proxy_page.edit_asset(asset)
            self.base.log_sentry("Event edit submission", resp)

        # todo: Test this
        if 'link' in add_data and add_data['link']:
            from tinker.admin.redirects import RedirectsView
            view = RedirectsView()
            path = str(asset['page']['parentFolderPath'] + "/" + asset['page']['name'])
            view.new_internal_redirect_submit(path, add_data['link'])

        # return redirect(url_for('events.EventsView:confirm'), code=302)
        return render_template("submit-confirm.html", eid=eid)

    @route('/api/reset-tinker-edits/<event_id>', methods=['get', 'post'])
    def reset_tinker_edits(self, event_id):
        my_page = self.base.read_page(event_id)

        asset, md, sd = my_page.get_asset()
        update(md, 'tinker-edits', '0')
        my_page.edit_asset(asset)

        return event_id

    def edit_all(self):
        type_to_find = 'system-page'
        xml_url = app.config['EVENTS_XML_URL']
        self.base.edit_all(type_to_find, xml_url)
        return 'success'

    # This endpoint is being re-added so that unit tests will be self-deleting. This endpoint is publicly visible, but
    # it is not referenced anywhere on any page, so the public shouldn't know of its existence.
    # Todo: this should require auth! otherwise, anyone could delete any event
    @route("/delete/<event_id>", methods=['GET'])
    def delete(self, event_id):
        event_page = self.base.read_page(event_id)
        response = event_page.delete_asset()
        self.base.unpublish(event_id, 'page')
        app.logger.debug(time.strftime("%c") + ": Event deleted by " + session['username'] + " " + str(response))
        self.base.publish(app.config['EVENT_XML_ID'])
        return render_template('events-delete-confirm.html')

    #This is the search for events to pare down what is being shown
    @route("/search", methods=['POST'])
    def search(self):
        # Start by declaring the variables from the index so that they can be passed into render_template
        show_create = True
        all_schools = OrderedDict({
            1: 'All Events',
            2: 'My Events',
            3: 'Other Events'},
            key=lambda t: t[0]
        )
        # The below can be added inside of the dictionary as they are built out
        # {4: 'College of Arts and Sciences'},
        # {5: 'College of Adult and Professional Studies'},
        # {6: 'Graduate School'},
        # {7: 'Bethel Seminary'},
        # {8: 'Administration with Faculty Status'},
        # {9: 'Other'}
        # Load the data, get the event type selection and title of the event the user is searching for
        data = json.loads(request.data)
        selection = data['selection']
        title = data['title']
        try:
            # Try converting the start date times to seconds representation
            start = datetime.datetime.strptime(data['start'], "%a %b %d %Y")

        except:
            # Set start and end to be falsey so that hasDates is set to false
            start = 0
        try:
            # Try converting the end date times to seconds representation
            end = datetime.datetime.strptime(data['end'], "%a %b %d %Y")
        except:
            # Set start and end to be falsey so that hasDates is set to false
            end = 0
        search_results, forms_header = self.base.get_search_results(selection, title, start, end)
        return render_template('search_results.html', list_of_events=search_results, formsHeader=forms_header)


EventsView.register(EventsBlueprint)
