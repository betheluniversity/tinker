#python


#flask
from flask import json as fjson
from flask import render_template
from flask import redirect

#local
from forms import EventForm
from cascade_events import *
from tinker import app


@app.route('/delete/<page_id>')
def delete_page(page_id):
    delete(page_id)
    return redirect('/', 302)


@app.route('/')
def show_home():
    ## index page for adding events and things
    username = get_user()
    forms = get_forms_for_user(username)
    return render_template('home.html', **locals())


@app.route("/add-event")
def form_index():
    username = get_user()
    form = EventForm()
    add_form = True
    return render_template('event-form.html', **locals())


@app.route("/read")
def read_page():
    get_user()
    client = get_client()

    identifier = {
        'id': '72aca6118c58651317cf8e74f03f11ab',
        'type': 'page'
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.read(auth, identifier)

    return "<pre>" + str(response) + "</pre>"


@app.route('/edit/event/<event_id>')
def edit_event_page(event_id):
    username = get_user()
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


@app.route("/submit", methods=['POST'])
def submit_form():
    username = get_user()
    form = EventForm()
    if not form.validate_on_submit():
        if 'event_id' in request.form.keys():
            event_id = request.form['event_id']
        else:
            #This error came from the add form because event_id wasn't set
            add_form = True
        return render_template('event-form.html', **locals())

    form = request.form
    #Get all the form data
    add_data = get_add_data(['general', 'offices', 'academic_dates', 'cas_departments', 'internal'], form)

    dates = get_dates(add_data)

    ##Add it to the dict, we can just ignore the old entries
    add_data['dates'] = dates

    username = get_user()

    asset = get_event_structure(add_data, username)

    resp = create(asset)

    return redirect('/', code=302)
    ##Just print the response for now
    ##return str(resp)


@app.route("/submit-edit", methods=['post'])
def submit_edit_form():
    username = get_user()
    form = EventForm()
    if not form.validate_on_submit():
        event_id = request.form['event_id']
        return render_template('event-form.html', **locals())

    form = request.form
    add_data = get_add_data(['general', 'offices', 'academic_dates', 'cas_departments', 'internal'], form)
    dates = get_dates(add_data)
    add_data['dates'] = dates
    event_id = form['event_id']

    username = get_user()

    asset = get_event_structure(add_data, username, event_id=event_id)

    current_year = get_current_year_folder(event_id)
    new_year = get_year_folder_value(add_data)

    resp = edit(asset)

    if new_year > current_year:
        resp = move_event_year(event_id, add_data)

    publish(event_id)
    publish(app.config['EVENT_XML_ID'])

    #return str(resp)
    return redirect('/', code=302)

