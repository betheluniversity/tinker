import time
from flask.ext.classy import FlaskView, route
from tinker.events.Events_Controller import EventsController
# from tinker.events.cascade_events import *
from flask import Blueprint, redirect, session, render_template, request, json as fjson, url_for
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
        # from cascade during hoempage load
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
        event_page = self.base.read_page(event_id)
        if event_page.is_in_workflow(event_id, asset_type='page'):
            return redirect(url_for('events.EventsView:event_in_workflow'), code=302)

        # import this here so we dont load all the content
        # from cascade during homepage load
        from tinker.events.forms import EventForm

        asset = self.base.read_page(event_id)
        self.base.get_edit_data(asset)

        # # Get the event data from cascade
        # event_data = self.base.read(event_id)
        #
        # # Get the different data sets from the response
        # form_data = event_data['asset']['page']
        # # the stuff from the data def
        # s_data = form_data['structuredData']['structuredDataNodes']['structuredDataNode']
        # # regular metadata
        # metadata = form_data['metadata']
        # # dynamic metadata
        # dynamic_fields = metadata['dynamicFields']['dynamicField']
        # # This dict will populate our EventForm object
        # edit_data = {}
        # date_count = 0
        # dates = {}
        # # Start with structuredDataNodes (data def content)
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
        #
        # # now metadata dynamic fields
        # for field in dynamic_fields:
        #     # This will fail if no metadata is set. It should be required but just in case
        #     if field.fieldValues:
        #         items = [item.value for item in field.fieldValues.fieldValue]
        #         edit_data[field.name.replace('-', '_')] = items
        #
        # # Add the rest of the fields. Can't loop over these kinds of metadata
        # edit_data['title'] = metadata.title
        # edit_data['teaser'] = metadata.metaDescription
        # author = metadata.author
        #
        # # Create an EventForm object with our data
        # form = EventForm(**edit_data)
        # form.event_id = event_id
        #
        # # convert dates to json so we can use Javascript to create custom DateTime fields on the form
        # dates = fjson.dumps(dates)

        return render_template('event-form.html', **locals())

    @route('/duplicate/<event_id>')
    # todo Michael will do duplicate
    def duplicate_event_page(self, event_id):
        # import this here so we dont load all the content
        # from cascade during homepage load
        from tinker.events.forms import EventForm

        # Get the event data from cascade
        event_data = read(event_id)

        # Get the different data sets from the response
        form_data = event_data.asset.page

        # the stuff from the data def
        s_data = form_data.structuredData.structuredDataNodes.structuredDataNode

        # regular metadata
        metadata = form_data.metadata

        # dynamic metadata
        dynamic_fields = metadata.dynamicFields.dynamicField

        # This dict will populate our EventForm object
        edit_data = {}
        date_count = 0
        dates = {}

        # Start with structuredDataNodes (data def content)
        for node in s_data:
            node_identifier = node.identifier.replace('-', '_')
            node_type = node.type
            if node_type == "text":
                edit_data[node_identifier] = node.text
            elif node_type == 'group':
                # These are the event dates. Create a dict so we can convert to JSON later.
                dates[date_count] = read_date_data_structure(node)
                date_count += 1
            elif node_identifier == 'image':
                edit_data['image'] = node.filePath

        # now metadata dynamic fields
        for field in dynamic_fields:
            # This will fail if no metadata is set. It should be required but just in case
            if field.fieldValues:
                items = [item.value for item in field.fieldValues.fieldValue]
                edit_data[field.name.replace('-', '_')] = items

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

    @route("/submit-edit", methods=['post'])
    def submit_edit_form(self):

        # import this here so we dont load all the content
        # from cascade during hoempage load
        from tinker.events.forms import EventForm

        form = EventForm()
        rform = request.form
        title = rform['title']
        username = session['username']
        # workflow = get_event_publish_workflow(title, username)
        workflow = None

        event_dates, dates_good, num_dates = self.base.check_event_dates(rform)

        failed = self.base.validate_form(rform, dates_good, event_dates, num_dates)
        if failed:
            return failed

        # ABOVE WAY INSTEAD?
        # if not form.validate_on_submit() or not dates_good:
        #     event_id = request.form['event_id']
        #     return render_template('event-form.html', **locals())

        form = rform
        add_data = self.base.get_add_data(metadata_list, form)
        dates = self.base.get_dates(add_data)
        add_data['event-dates'] = dates
        add_data['author'] = request.form['author']
        event_id = form['event_id']

        asset = self.base.get_event_structure(add_data, username, workflow=workflow, event_id=event_id)

        current_year = self.base.get_current_year_folder(event_id)
        new_year = self.base.get_year_folder_value(add_data)

        proxy_page = self.base.read_page(event_id)
        response = proxy_page.edit_asset(asset)
        self.base.log_sentry("Event edit submission", response)

        if new_year > current_year:
            response = self.base.move_event_year(event_id, add_data)
            app.logger.debug(time.strftime("%c") + ": Event move submission by " + username + " " + str(response))

        # 'link' must be a valid component
        if 'link' in add_data and add_data['link'] != "":
            from tinker.admin.redirects import new_internal_redirect_submit
            path = str(asset['page']['parentFolderPath'] + "/" + asset['page']['name'])
            new_internal_redirect_submit(path, add_data['link'])

        return redirect('/event/confirm', code=302)

    @route("/submit", methods=['post'])
    def submit_form(self):

        # import this here so we dont load all the content
        # from cascade during homepage load
        from tinker.events.forms import EventForm

        # form = EventForm()
        rform = request.form
        # title = rform['title']
        username = session['username']
        workflow = None
        # workflow = self.base.get_event_publish_workflow(title, username)

        # create a dict of date values so we can access them in Jinja later.
        # they aren't part of the form so we can't just do form.start1, etc...
        event_dates, dates_good, num_dates = self.base.check_event_dates(rform)

        failed = self.base.validate_form(rform, dates_good, event_dates, num_dates)
        if failed:
            return failed

        # Get all the form data

        from events_metadata import metadata_list
        add_data = self.base.get_add_data(metadata_list, rform)

        dates = self.base.get_dates(add_data)

        # Add it to the dict, we can just ignore the old entries
        add_data['event-dates'] = dates

        # took out workflow=workflow parameter is it NEEDED?
        asset = self.base.get_event_structure(add_data, username, workflow=workflow)

        resp = self.base.create(asset)

        if username == 'amf39248':
            app.logger.debug(time.strftime("%c") + ": TESTING" + asset)
            app.logger.debug(time.strftime("%c") + ": TESTING" + resp)

        self.base.link(add_data, asset)

        return redirect('/event/confirm', code=302)

    @route('/api/reset-tinker-edits/<event_id>', methods=['get', 'post'])
    def reset_tinker_edits(self, event_id):
        ws_connector = self.base.Cascade(app.config['SOAP_URL'], app.config['AUTH'], app.config['SITE_ID'])
        my_page = self.base.Page(ws_connector, event_id)

        asset, md, sd = my_page.get_asset()
        self.base.update(md, 'tinker-edits', '0')
        my_page.edit_asset(asset)

        return event_id

    # # todo this is a test, delete later
    # def tim(self):
    #     return str(self.base.copy_folder('/_testing/tim-heck/test-event-folder3', 'f21ae7948c5865137725e12f0f26d863'))

EventsView.register(EventsBlueprint)
