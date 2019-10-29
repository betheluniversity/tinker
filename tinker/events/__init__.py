# Global
import datetime
import json
import time

# Packages
from bu_cascade.asset_tools import update
from flask import redirect, session, render_template, request, url_for
from flask_classy import FlaskView, route
from collections import OrderedDict

# Local
from tinker.events.events_metadata import metadata_list
from tinker import app, cache
from tinker.events.events_controller import EventsController


class EventsView(FlaskView):
    route_base = '/events'

    def __init__(self):
        self.base = EventsController()
        self.base.datetime_format = "%B %d %Y, %I:%M %p"

    # Allows any user to access events
    def before_request(self, name, **kwargs):
        pass

    def index(self):
        username = session['username']

        @cache.memoize(timeout=300)
        def index_cache(username):
            show_create = True
            if 'Tinker Events - CAS' in session['groups'] or 'Event Approver' in session['groups']:
                # The special admin view
                all_schools = OrderedDict({
                    1: 'My Events',
                    2: 'All Events',
                    3: 'Other Events'},
                    key=lambda t: t[0]
                )
            else:
                all_schools = OrderedDict({
                    1: 'User Events'}
                )

            return render_template('events/home.html', show_create=show_create, all_schools=all_schools, list_of_events=None,
                                   formsHeader="All Events")

        return index_cache(username)

    def confirm(self):
        return render_template('events/submit-confirm.html', **locals())

    def event_in_workflow(self):
        return render_template('events/in-workflow.html')

    # CANT CACHE THIS
    def add(self):
        # import this here so we dont load all the content from cascade during homepage load
        from tinker.events.forms import EventForm

        form = EventForm()
        new_form = True
        return render_template('events/form.html', **locals())

    def edit(self, event_id):
        # if the event is in a workflow currently, don't allow them to edit. Instead, redirect them.
        if self.base.asset_in_workflow(event_id, asset_type='page'):
            return redirect(url_for('EventsView:event_in_workflow'), code=302)

        edit_data, dates = self.base.build_edit_form(event_id)
        # todo: fix this with the submit_all() functionality ASK CALEB
        # convert 'On/Off campus' to 'On/Off Campus' for all events
        from tinker.events.forms import EventForm
        form = EventForm(**edit_data)
        if 'location' in edit_data and edit_data['location']:
            edit_data['location'].replace(' c', ' C')

        return render_template('events/form.html', **locals())

    def duplicate(self, event_id):
        edit_data, dates = self.base.build_edit_form(event_id)
        from tinker.events.forms import EventForm
        form = EventForm(**edit_data)
        new_form = True

        return render_template('events/form.html', **locals())

    @route("/submit", methods=['post'])
    def submit(self):
        rform = self.base.dictionary_encoder.encode(request.form)
        username = session['username']
        eid = rform.get('event_id')
        dates, num_dates = self.base.get_event_dates(rform)
        dates_str, dates_good = self.base.check_event_dates(dates)
        form, passed = self.base.validate_form(rform.internal_dictionary(), dates_good)
        workflow = self.base.create_workflow(app.config['EVENTS_WORKFLOW_ID'], session['username'] + '--' + rform['title'] + ', ' + datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p"))

        if not passed:
            if 'event_id' in rform.keys():
                event_id = rform['event_id']
            else:
                new_form = True
            author = rform["author"]
            num_dates = int(rform['num_dates'])

            return render_template('events/form.html', **locals())

        add_data, asset, eid = self.base.submit_new_or_edit(rform, username, eid, dates, num_dates, metadata_list, workflow)

        # todo: Test this
        if 'link' in add_data and add_data['link']:
            from tinker.admin.redirects import RedirectsView
            view = RedirectsView()
            path = str(asset['page']['parentFolderPath'] + "/" + asset['page']['name'])
            view.new_internal_redirect_submit(path, add_data['link'])

        return render_template("events/submit-confirm.html", **locals())

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
        self.base.cascade_call_logger(locals())
        self.base.unpublish(event_id, 'page')
        app.logger.debug(time.strftime("%c") + ": Event deleted by " + session['username'] + " " + str(response))
        self.base.publish(app.config['EVENT_XML_ID'])
        return render_template('events/delete-confirm.html')

    # This is the search for events to pare down what is being shown
    @route("/search", methods=['POST'])
    def search(self):
        # Load the data, get the event type selection and title of the event the user is searching for
        data = self.base.dictionary_encoder.encode(json.loads(request.data))
        selection = data['selection']
        title = data['title']
        try:
            start = datetime.datetime.strptime(data['start'], "%a %b %d %Y")
        except:
            start = 0
        try:
            end = datetime.datetime.strptime(data['end'], "%a %b %d %Y")
        except:
            end = 0

        search_results, forms_header = self.base.get_search_results(selection, title, start, end)
        search_results.sort(key=lambda event: event['event-dates'][0], reverse=False)
        return render_template('events/search-results.html', list_of_events=search_results, formsHeader=forms_header)
