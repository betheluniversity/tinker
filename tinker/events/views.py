#python
import json

#flask
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import request
from flask import json as fjson

from tinker.events.cascade_events import *
from tinker import app
from tinker import tools

event_blueprint = Blueprint('event', __name__,
                        template_folder='templates')


@event_blueprint.route('/')
def home():
    forms = get_forms_for_user(session['username'])
    return render_template('events-home.html', **locals())

@event_blueprint.route('/delete/<page_id>')
def delete_page(page_id):
    workflow = get_event_delete_workflow()
    delete(page_id, workflow)
    publish_event_xml()
    return redirect('/event/delete-confirm', code=302)


@event_blueprint.route('/delete-confirm')
def delete_confirm():
    return render_template('events-delete-confirm.html', **locals())


@event_blueprint.route("/add")
def form_index():

    ##import this here so we dont load all the content
    ##from cascade during hoempage load
    from tinker.events.forms import EventForm

    form = EventForm()
    add_form = True
    return render_template('event-form.html', **locals())


@event_blueprint.route("/read")
def read_page():
    tools.get_user()
    client = get_client()

    identifier = {
        # 'id': '85d64f148c5865130c130b3a6d2babc5',
        'type': 'folder',
        'path': '/'
    }


    auth = app.config['CASCADE_LOGIN']
    response = client.service.read(auth, identifier)

    return "<pre>" + str(response) + "</pre>"
    # return str(response)

@event_blueprint.route('/edit/<event_id>')
def edit_event_page(event_id):

    ##import this here so we dont load all the content
    ##from cascade during hoempage load
    from tinker.events.forms import EventForm

    #Get the event data from cascade
    event_data = read(event_id)

    #Get the different data sets from the response

    form_data = event_data.asset.page
    #the stuff from the data def
    s_data = form_data.structuredData.structuredDataNodes.structuredDataNode
    #regular metadata
    metadata = form_data.metadata
    #dynamic metadata
    dynamic_fields = metadata.dynamicFields.dynamicField
    #This dict will populate our EventForm object
    edit_data = {}
    date_count = 0
    dates = {}
    #Start with structuredDataNodes (data def content)
    for node in s_data:
        node_identifier = node.identifier.replace('-', '_')
        node_type = node.type
        if node_type == "text":
            edit_data[node_identifier] = node.text
        elif node_type == 'group':
            ## These are the event dates. Create a dict so we can convert to JSON later.
            date_data = read_date_data_structure(node)
            dates[date_count] = date_data
            date_count += 1

    #now metadata dynamic fields
    for field in dynamic_fields:
        #This will fail if no metadata is set. It should be required but just in case
        if field.fieldValues:
            items = [item.value for item in field.fieldValues.fieldValue]
            edit_data[field.name.replace('-', '_')] = items

    ## Add the rest of the fields. Can't loop over these kinds of metadata
    edit_data['title'] = metadata.title
    edit_data['teaser'] = metadata.metaDescription

    #Create an EventForm object with our data
    form = EventForm(**edit_data)
    form.event_id = event_id

    #convert dates to json so we can use Javascript to create custom DateTime fields on the form
    dates = fjson.dumps(dates)

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

    #convert event dates to JSON
    return json.dumps(event_dates), dates_good, num_dates

@event_blueprint.route("/submit", methods=['POST'])
def submit_form():

    ##import this here so we dont load all the content
    ##from cascade during hoempage load
    from tinker.events.forms import EventForm

    form = EventForm()
    rform = request.form
    title = rform['title']
    username = session['username']
    workflow = get_event_publish_workflow(title, username)

    #check event dates here?

    #create a dict of date values so we can access them in Jinja later.
    #they aren't part of the form so we can't just do form.start1, etc...
    event_dates, dates_good, num_dates = check_event_dates(rform)

    dates = []

    if not form.validate_on_submit() or not dates_good:
        if 'event_id' in request.form.keys():
            event_id = request.form['event_id']
        else:
            #This error came from the add form because event_id wasn't set
            add_form = True
        return render_template('event-form.html', **locals())

    form = rform
    #Get all the form data
    add_data = get_add_data(['general', 'offices', 'academic_dates', 'cas_departments', 'internal'], form)

    dates = get_dates(add_data)

    ##Add it to the dict, we can just ignore the old entries
    add_data['dates'] = dates

    asset = get_event_structure(add_data, username, workflow)

    resp = create(asset)

    return redirect('/event/confirm', code=302)
    ##Just print the response for now


@event_blueprint.route("/submit-edit", methods=['post'])
def submit_edit_form():

    ##import this here so we dont load all the content
    ##from cascade during hoempage load
    from tinker.events.forms import EventForm

    form = EventForm()
    rform = request.form
    title = rform['title']
    username = session['username']
    workflow = get_event_publish_workflow(title, username)

    event_dates, dates_good, num_dates = check_event_dates(rform)

    if not form.validate_on_submit()or not dates_good:
        event_id = request.form['event_id']
        return render_template('event-form.html', **locals())

    form = rform
    add_data = get_add_data(['general', 'offices', 'academic_dates', 'cas_departments', 'internal'], form)
    dates = get_dates(add_data)
    add_data['dates'] = dates
    event_id = form['event_id']

    asset = get_event_structure(add_data, username, workflow=workflow, event_id=event_id)

    current_year = get_current_year_folder(event_id)
    new_year = get_year_folder_value(add_data)

    resp = edit(asset)
    app.logger.warn(time.strftime("%c") + ": Event edit submission by " + username + " " + str(resp))

    if new_year > current_year:
        resp = move_event_year(event_id, add_data)
        app.logger.warn(time.strftime("%c") + ": Event movesubmission by " + username + " " + str(resp))


    #return str(resp)
    return redirect('/event/confirm', code=302)


@event_blueprint.route('/confirm')
def confirm():
    return render_template('submit-confirm.html', **locals())
