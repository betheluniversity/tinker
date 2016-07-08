import time
from flask.ext.classy import FlaskView, route
from tinker.events.Events_Controller import EventsController
from bu_cascade.asset_tools import update
# from tinker.events.cascade_events import *
from flask import Blueprint, redirect, session, render_template, request, url_for
from tinker import app
from events_metadata import metadata_list

EventsBlueprint = Blueprint('events', __name__, template_folder='templates')


class EventsView(FlaskView):
    route_base = '/event'

    def __init__(self):
        self.base = EventsController()

    # Allows any user to access events
    def before_request(self, name, **kwargs):
        pass

    def index(self):
        forms = self.base.get_forms_for_user(session['username'])
        if 'Event Approver' in session['groups']:
            event_approver_forms = self.base.get_forms_for_event_approver()
        return render_template('events-home.html', **locals())

    def delete_confirm(self):
        return render_template('events-delete-confirm.html', **locals())

    def confirm(self):
        return render_template('submit-confirm.html', **locals())

    def event_in_workflow(self):
        return render_template('event-in-workflow.html')

    def add(self):
        # import this here so we dont load all the content
        # from cascade during homepage load
        from tinker.events.forms import EventForm

        form = EventForm()
        add_form = True
        return render_template('event-form.html', **locals())

    @route('/delete/<page_id>')
    def delete_page(self, page_id):
        event_page = self.base.read_page(page_id)
        response = event_page.delete_asset()
        app.logger.debug(time.strftime("%c") + ": New folder creation by " + session['username'] + " " + str(response))
        self.base.publish(app.config['EVENT_XML_ID'])
        return redirect(url_for('events.EventsView:delete_confirm'), code=302)

    @route('/edit/<event_id>')
    def edit_event_page(self, event_id):
        # if the event is in a workflow currently, don't allow them to edit. Instead, redirect them.
        if self.base.asset_in_workflow(event_id, asset_type='page'):
            return redirect(url_for('events.EventsView:event_in_workflow'), code=302)

        edit_data, form, dates, author = self.base.build_edit_form(event_id)
        # todo convert 'On/Off campus' to 'On/Off Campus' for all events
        if edit_data['location']:
            edit_data['location'].replace(' c', ' C')

        return render_template('event-form.html', **locals())

    @route('/duplicate/<event_id>')
    def duplicate_event_page(self, event_id):
        edit_data, form, dates, author = self.base.build_edit_form(event_id)

        add_form = True

        return render_template('event-form.html', **locals())

    @route("/submit/<edit>", methods=['post'])
    @route("/submit", methods=['post'])
    def submit_form(self, edit=False):
        rform = request.form
        username = session['username']
        workflow = None
        eid = rform.get('event_id')
        # workflow = self.base.get_event_publish_workflow(title, username)
        event_dates, dates_good, num_dates = self.base.check_event_dates(rform)
        failed = self.base.validate_form(rform, dates_good)
        if failed:
            return failed

        if not eid:
            bid = app.config['EVENTS_BASE_ASSET']
            event_data, metadata, structured_data = self.base.cascade_connector.load_base_asset_by_id(bid, 'page')
            # Get all the form data
            add_data = self.base.get_add_data(metadata_list, rform)
            dates = self.base.get_dates(add_data)

            add_data['event-dates'] = dates
            asset = self.base.get_event_structure(event_data, metadata, structured_data, add_data, username, workflow=workflow)
            response = self.base.create(asset)

        else:
            page = self.base.read_page(eid)
            event_data, metadata, structured_data = page.get_asset()
            # Get all the form data
            add_data = self.base.get_add_data(metadata_list, rform)
            dates = self.base.get_dates(add_data)

            add_data['event-dates'] = dates
            add_data['author'] = request.form['author']
            event_id = rform['event_id']
            asset = self.base.get_event_structure(event_data, metadata, structured_data, add_data, username, workflow=workflow, event_id=event_id)
            current_year = self.base.get_current_year_folder(event_id)
            new_year = self.base.get_year_folder_value(add_data)
            proxy_page = self.base.read_page(event_id)
            response = proxy_page.edit_asset(asset)
            self.base.log_sentry("Event edit submission", response)

            if new_year > current_year:
                response = self.base.move_event_year(event_id, add_data)
                app.logger.debug(time.strftime("%c") + ": Event move submission by " + username + " " + str(response))

        # Checks if the link is valid
        if 'link' in add_data and add_data['link'] != "":
            from tinker.admin.redirects import new_internal_redirect_submit
            path = str(asset['page']['parentFolderPath'] + "/" + asset['page']['name'])
            new_internal_redirect_submit(path, add_data['link'])

        return redirect(url_for('events.EventsView:confirm'), code=302)

    @route('/api/reset-tinker-edits/<event_id>', methods=['get', 'post'])
    def reset_tinker_edits(self, event_id):
        ws_connector = self.base.Cascade(app.config['SOAP_URL'], app.config['AUTH'], app.config['SITE_ID'])
        my_page = self.base.Page(ws_connector, event_id)

        asset, md, sd = my_page.get_asset()
        update(md, 'tinker-edits', '0')
        my_page.edit_asset(asset)

        return event_id

    # # todo this is a test, delete later
    # def tim(self):
    #     return str(self.base.copy_folder('/_testing/tim-heck/test-event-folder3', 'f21ae7948c5865137725e12f0f26d863'))

EventsView.register(EventsBlueprint)
