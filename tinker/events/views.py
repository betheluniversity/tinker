# python
import json
from werkzeug.utils import secure_filename

# flask
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import request
from flask import json as fjson

from tinker.events.cascade_events import *
from tinker import app
from tinker import tools

event_blueprint = Blueprint('event', __name__, template_folder='templates')


@event_blueprint.route('/')
def home():
    forms = get_forms_for_user(session['username'])
    if 'Event Approver' in tools.get_groups_for_user():
        event_approver_forms = get_forms_for_event_approver()
    return render_template('events-home.html', **locals())


@event_blueprint.route('/delete/<page_id>')
def delete_page(page_id):
    workflow = get_event_delete_workflow()
    delete(page_id, workflow=workflow)
    publish_event_xml()
    return redirect('/event/delete-confirm', code=302)


@event_blueprint.route('/delete-confirm')
def delete_confirm():
    return render_template('events-delete-confirm.html', **locals())


@event_blueprint.route("/add")
def form_index():

    # import this here so we dont load all the content
    # from cascade during hoempage load
    from tinker.events.forms import EventForm

    form = EventForm()
    add_form = True
    return render_template('event-form.html', **locals())


@event_blueprint.route("/read")
def read_page():
    tools.get_user()
    client = get_client()
    identifier = {
        'id': '3967ee858c58651337aebe3f9560b791',
        'type': 'block',
        # 'path': {
        #     'path': '/',
        #     'siteId': app.config['SITE_ID']
        # }
    }


    auth = app.config['CASCADE_LOGIN']
    response = client.service.read(auth, identifier)

    return "<pre>" + str(response) + "</pre>"


@event_blueprint.route('/in-workflow')
def event_in_workflow():
    return render_template('event-in-workflow.html')


@event_blueprint.route('/edit/<event_id>')
def edit_event_page(event_id):
    # if the event is in a workflow currently, don't allow them to edit. Instead, redirect them.
    if is_asset_in_workflow(event_id):
        return redirect('/event/in-workflow', code=302)

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

    return render_template('event-form.html', **locals())


@event_blueprint.route('/duplicate/<event_id>')
def duplicate_event_page(event_id):

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


def check_event_dates(form):

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


@event_blueprint.route("/submit", methods=['POST'])
def submit_form():

    # import this here so we dont load all the content
    # from cascade during hoempage load
    from tinker.events.forms import EventForm

    form = EventForm()
    rform = request.form
    title = rform['title']
    username = session['username']
    workflow = get_event_publish_workflow(title, username)

    # check event dates here?

    # create a dict of date values so we can access them in Jinja later.
    # they aren't part of the form so we can't just do form.start1, etc...
    event_dates, dates_good, num_dates = check_event_dates(rform)

    dates = []

    if not form.validate_on_submit() or not dates_good:
        if 'event_id' in request.form.keys():
            event_id = request.form['event_id']
        else:
            # This error came from the add form because event_id wasn't set
            add_form = True
        return render_template('event-form.html', **locals())

    form = rform
    # Get all the form data
    metadata_list = ['general', 'offices', 'cas_departments', 'internal']
    add_data = get_add_data(metadata_list, form)

    dates = get_dates(add_data)

    # Add it to the dict, we can just ignore the old entries
    add_data['event-dates'] = dates

    asset = get_event_structure(add_data, username, workflow)

    resp = create(asset)

    # 'link' must be a valid component
    if 'link' in add_data and add_data['link'] != "":
        from tinker.redirects.views import new_internal_redirect_submit
        path = str(asset['page']['parentFolderPath'] + "/" + asset['page']['name'])
        new_internal_redirect_submit(path, add_data['link'])

    return redirect('/event/confirm', code=302)
    # Just print the response for now


@event_blueprint.route("/submit-edit", methods=['post'])
def submit_edit_form():

    # import this here so we dont load all the content
    # from cascade during hoempage load
    from tinker.events.forms import EventForm

    form = EventForm()
    rform = request.form
    title = rform['title']
    username = session['username']
    workflow = get_event_publish_workflow(title, username)

    event_dates, dates_good, num_dates = check_event_dates(rform)

    if not form.validate_on_submit() or not dates_good:
        event_id = request.form['event_id']
        return render_template('event-form.html', **locals())

    form = rform
    add_data = get_add_data(['general', 'offices', 'cas_departments', 'internal'], form)
    dates = get_dates(add_data)
    add_data['event-dates'] = dates
    add_data['author'] = request.form['author']
    event_id = form['event_id']

    asset = get_event_structure(add_data, username, workflow=workflow, event_id=event_id)

    current_year = get_current_year_folder(event_id)
    new_year = get_year_folder_value(add_data)


    resp = edit(asset)
    app.logger.warn(time.strftime("%c") + ": Event edit submission by " + username + " with id " + event_id + ". " + str(resp))

    if new_year > current_year:
        resp = move_event_year(event_id, add_data)
        app.logger.warn(time.strftime("%c") + ": Event move submission by " + username + " " + str(resp))

    # 'link' must be a valid component
    if 'link' in add_data and add_data['link'] != "":
        from tinker.redirects.views import new_internal_redirect_submit
        path = str(asset['page']['parentFolderPath'] + "/" + asset['page']['name'])
        new_internal_redirect_submit(path, add_data['link'])

    return redirect('/event/confirm', code=302)


@event_blueprint.route('/confirm')
def confirm():
    return render_template('submit-confirm.html', **locals())