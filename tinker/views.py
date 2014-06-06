#python

#flask
from flask import render_template
from flask import request
from flask import redirect

#local
from forms import EventForm
from cascade_events import *
from tools import get_client

from tinker import app


@app.route('/delete/<page_id>')
def delete_page(page_id):
    resp = delete(page_id)
    return str(resp)


@app.route('/')
def show_home():
    ## index page for adding events and things
    forms = get_forms_for_user('ejc84332')

    return render_template('home.html', **locals())


@app.route("/add")
def form_index():

    form = EventForm()
    add_form = True
    return render_template('event-form.html', **locals())


@app.route("/read")
def read_page():

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

    #Start with structuredDataNodes (data def content)
    for node in s_data:
        node_identifier = node.identifier.replace('-', '_')
        node_type = node.type
        if node_type == "text":
            edit_data[node_identifier] = node.text
        elif node_type == 'group':
            ## These are the event dates
            node_data = node.structuredDataNodes.structuredDataNode
            date_data = {}
            for date in node_data:
                date_data[date.identifier] = date.text
            edit_data[node_identifier] = date_data

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

    return render_template('event-form.html', **locals())


@app.route("/submit", methods=['POST'])
def submit_form():

    form = EventForm()
    if not form.validate_on_submit():
        event_id = request.form['event_id']
        return render_template('event-form.html', **locals())

    form = request.form
    #Get all the form data
    add_data = get_add_data(['general', 'offices', 'academic_dates', 'cas_departments', 'internal'], form)

    dates = get_dates(add_data)

    ##Add it to the dict, we can just ignore the old entries
    add_data['dates'] = dates

    asset = get_event_structure(add_data)

    resp = create(asset)

    code = re.search('createdAssetId = "(.*?)"', str(resp)).group(1)

    return redirect('/', code=302)
    ##Just print the response for now
    ##return resp


@app.route("/submit-edit", methods=['post'])
def submit_edit_form():

    form = EventForm()
    if not form.validate_on_submit():
        event_id = request.form['event_id']
        return render_template('event-form.html', **locals())

    form = request.form
    add_data = get_add_data(['general', 'offices', 'academic_dates', 'cas_departments', 'internal'], form)
    dates = get_dates(add_data)
    add_data['dates'] = dates

    asset = get_event_structure(add_data, event_id=form['event_id'])

    resp = edit(asset)

    publish(form['event_id'])
    publish(app.config['EVENT_XML_ID'])

    #return str(resp)
    return redirect('/', code=302)



