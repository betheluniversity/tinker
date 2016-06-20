__author__ = 'ejc84332'

import json
from flask.ext.classy import FlaskView, route
from tinker.events.Events_Controller import EventsController
from flask import Blueprint, redirect, session, render_template, app, request, json
# from tinker.events.cascade_events import *
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
        # workflow = get_event_delete_workflow()
        # delete(page_id, workflow=workflow)
        self.base.delete(page_id)
        # publish_event_xml()
        self.base.publish(app.config['EVENT_XML_ID'])
        return redirect('/events/delete_confirm', code=302)

    def edit_event_page(self, event_id):
        # if the event is in a workflow currently, don't allow them to edit. Instead, redirect them.
        # asset type='block'?
        if self.base.asset_in_workflow(event_id, asset_type='block'):
            return redirect('/event/in-workflow', code=302)

        # import this here so we dont load all the content
        # from cascade during homepage load
        from tinker.events.forms import EventForm

        event_block = self.base.read_block(event_id)
        event_data = event_block.read_asset()

        form_data, s_data = event_block.read_asset()
        # Get the event data from cascade
        event_data = self.base.read(event_id)
        edit_data = self.base.get_edit_data(event_data)
        # Get the different data sets from the response
        form_data = event_data.asset.page

        # the stuff from the data def
        # s_data = form_data.structuredData.structuredDataNodes.structuredDataNode
        s_data = form_data["structuredData"]["structuredDataNodes"]["structuredDataNode"]
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
        # todo should the date be in the tinker controller?
            elif node_type == 'group':
                # These are the event dates. Create a dict so we can convert to JSON later.
                dates[date_count] = read_date_data_structure(node)
                date_count += 1
            elif node_identifier == 'image':
                edit_data['image'] = node.filePath
        #
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
        # todo is this date getting what I think it is?
        # todo what is fjson vs. json?
        dates = fjson.dumps(edit_data.date)

        return render_template('event-form.html', **locals())

    def check_event_dates(self, form):

        event_dates = {}
        dates_good = False
        num_dates = int(form['num_dates'])
        for x in range(1, num_dates+1):  # the page doesn't use 0-based indexing

            i = str(x)
            start_l = 'start' + i
            end_l = 'end' + i
            all_day_l = 'allday' + i

            start = form[start_l]
            end = form[end_l]
            all_day = all_day_l in form.keys()

            event_dates[start_l] = start
            event_dates[end_l] = end
            event_dates[all_day_l] = all_day

            start_and_end = start and end

            if start_and_end:
                dates_good = True

        # convert event dates to JSON
        return json.dumps(event_dates), dates_good, num_dates

    # @route('/duplicate/<event_id>')
    def duplicate_event_page(self, event_id):

        if self.base.asset_in_workflow(event_id, asset_type='block'):
            return redirect('/event/in-workflow', code=302)

        # import this here so we dont load all the content
        # from cascade during homepage load
        from tinker.events.forms import EventForm

        event_block = self.base.read_block(event_id)
        event_data = event_block.read_asset()
        edit_data = self.base.get_edit_data(event_data)

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
        # # This dict will populate our EventForm object
        # edit_data = {}
        # date_count = 0
        # dates = {}
        # # Start with structuredDataNodes (data def content)
        # self.base.node(s_data, edit_data, date_count, dates)
        #
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
        # self.base.metadata(dynamic_fields, edit_data)
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

        # convert dates to json so we can use Javascript to create custom DateTime fields on the form
        # todo figure out how to get dates
        # todo fjson vs json?
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
        workflow = self.base.get_event_publish_workflow(title, username)

        event_dates, dates_good, num_dates = self.base.check_event_dates(rform)

        failed = self.base.validate_form(rform, dates_good)
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

        resp = self.base.edit(asset)
        self.base.log_sentry("Event edit submission", resp)

        if new_year > current_year:
            resp = self.base.move_event_year(event_id, add_data)
            app.logger.debug(self.base.time.strftime("%c") + ": Event move submission by " + username + " " + str(resp))

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

        form = EventForm()
        rform = request.form
        eid = rform.get('event_id')
        title = rform['title']
        username = session['username']
        workflow = None
        # workflow = self.base.get_event_publish_workflow(title, username)

        # create a dict of date values so we can access them in Jinja later.
        # they aren't part of the form so we can't just do form.start1, etc...
        event_dates, dates_good, num_dates = self.base.check_event_dates(rform)

        # dates = []

        failed = self.base.validate_form(rform, dates_good)
        if failed:
            return failed

        if not form.validate_on_submit() or not dates_good:
            if 'event_id' in request.form.keys():
                event_id = request.form['event_id']
            else:
                # This error came from the add form because event_id wasn't set
                add_form = True
            return render_template('event-form.html', **locals())

        # Get all the form data

        from events_metadata import metadata_list
        add_data = self.base.get_add_data(metadata_list, rform)

        dates = self.base.get_dates(add_data)

        # Add it to the dict, we can just ignore the old entries
        add_data['event-dates'] = dates

        # took out workflow=workflow parameter is it NEEDED?
        asset = self.base.get_event_structure(add_data, username, workflow)

        resp = self.base.create(asset)

        if username == 'amf39248':
            app.logger.debug(self.base.time.strftime("%c") + ": TESTING" + asset)
            app.logger.debug(self.base.time.strftime("%c") + ": TESTING" + resp)

        self.base.link(add_data, asset)

        # 'link' must be a valid component
        if 'link' in add_data and add_data['link'] != "":
            from tinker.admin.redirects import new_internal_redirect_submit
            path = str(asset['page']['parentFolderPath'] + "/" + asset['page']['name'])
            new_internal_redirect_submit(path, add_data['link'])

        return redirect('/event/confirm', code=302)
        # Just print the response for now

    # def post(self):
    #
    #     rform = request.form
    #     eaid = rform.get('e_announcement_id')
    #
    #     failed = self.base.validate_form(rform)
    #     if failed:
    #         return failed
    #
    #     if not eaid:
    #         bid = app.config['E_ANN_BASE_ASSET']
    #         e_announcement_data, mdata, sdata = self.base.cascade_connector.load_base_asset_by_id(bid, 'block')
    #         asset = self.base.update_structure(e_announcement_data, sdata, rform, e_announcement_id=eaid)
    #         resp = self.base.create_block(asset)
    #         self.base.log_sentry('New e-announcement submission', resp)
    #         return redirect(url_for('e-announcements.EAnnouncementsView:confirm', status='new'), code=302)
    #
    #     else:
    #         block = self.base.read_block(eaid)
    #         e_announcement_data, mdata, sdata = block.read_asset()
    #         asset = self.base.update_structure(e_announcement_data, sdata, rform, e_announcement_id=eaid)
    #         resp = str(block.edit_asset(asset))
    #         self.base.log_sentry("E-Announcement edit submission", resp)
    #         return redirect(url_for('e-announcements.EAnnouncementsView:confirm', status='edit'), code=302)

    @route('/api/reset-tinker-edits/<event_id>', methods=['get', 'post'])
    def reset_tinker_edits(self, event_id):
        ws_connector = self.base.Cascade(app.config['SOAP_URL'], app.config['AUTH'], app.config['SITE_ID'])
        my_page = self.base.Page(ws_connector, event_id)

        asset, md, sd = my_page.get_asset()
        self.base.update(md, 'tinker-edits', '0')
        my_page.edit_asset(asset)

        return event_id

EventsView.register(EventsBlueprint)
