#python
import json

#flask
from flask import render_template
from flask import redirect

from cascade_events import *
from cascade_faculty_bio import *

from tinker import app


@app.route('/delete/<page_id>')
def delete_page(page_id):
    workflow = get_event_delete_workflow()
    delete(page_id, workflow)
    return redirect('/', 302)


@app.route('/')
def show_home():
    ## index page for adding events and things
    username = get_user()
    forms = get_forms_for_user(username)
    return render_template('home.html', **locals())


@app.route('/confirm')
def confirm():
    return render_template('/confirm/submit-confirm.html', **locals())


@app.route("/add-event")
def form_index():

    ##import this here so we dont load all the content
    ##from cascade during homepage load
    from forms import EventForm

    username = get_user()
    form = EventForm()
    add_form = True
    return render_template('event-form.html', **locals())


@app.route('/test')
def test():
    get_user()
    client = get_client()

    identifier = {
        'id': 'aab8e27c8c5865131315e7c4e7a092a5',
        'type': 'page'
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.read(auth, identifier)

    return "%s" % str(response)


@app.route("/read")
def read_page():
    get_user()
    client = get_client()

    identifier = {
        'id': 'cb95d9088c58651375fc4ed23144e4d4',
        'type': 'page'
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.read(auth, identifier)

    return "<pre>" + str(response) + "</pre>"


@app.route('/event/edit/<event_id>')
def edit_event_page(event_id):

    ##import this here so we dont load all the content
    ##from cascade during hoempage load
    from forms import EventForm

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

@app.route("/submit", methods=['POST'])
def submit_event_form():

    ##import this here so we dont load all the content
    ##from cascade during hoempage load
    from forms import EventForm

    username = get_user()
    form = EventForm()
    rform = request.form
    workflow = get_event_publish_workflow()

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

    username = get_user()

    asset = get_event_structure(add_data, username, workflow)

    resp = create(asset)
    app.logger.warn(time.strftime("%c") + ": new event submission " + str(resp))
    return redirect('/confirm', code=302)
    ##Just print the response for now


@app.route("/submit-edit", methods=['post'])
def submit_edit_form():

    ##import this here so we dont load all the content
    ##from cascade during hoempage load
    from forms import EventForm

    username = get_user()
    form = EventForm()
    rform = request.form
    workflow = get_event_publish_workflow()

    event_dates, dates_good, num_dates = check_event_dates(rform)

    if not form.validate_on_submit()or not dates_good:
        event_id = request.form['event_id']
        return render_template('event-form.html', **locals())

    form = rform
    add_data = get_add_data(['general', 'offices', 'academic_dates', 'cas_departments', 'internal'], form)
    dates = get_dates(add_data)
    add_data['dates'] = dates
    event_id = form['event_id']

    username = get_user()

    asset = get_event_structure(add_data, username, workflow=workflow, event_id=event_id)

    current_year = get_current_year_folder(event_id)
    new_year = get_year_folder_value(add_data)

    resp = edit(asset)
    app.logger.warn(time.strftime("%c") + ": event edit submission " + str(resp))

    if new_year > current_year:
        resp = move_event_year(event_id, add_data)
        app.logger.warn(time.strftime("%c") + ": event movesubmission " + str(resp))


    #return str(resp)
    return redirect('/', code=302)

@app.route("/faculty-bio")
def faculty_bio_home():

    ## index page for adding events and things
    username = get_user()

    forms = get_faculty_bios_for_user(username)
    return render_template('faculty-bio-home.html', **locals())

@app.route("/faculty-bio/edit/new")
def faculty_bio_new_form():

    ##import this here so we dont load all the content
    ##from cascade during homepage load
    from forms import FacultyBioForm

    username = get_user()

    form = FacultyBioForm()

    add_form = True
    return render_template('faculty-bio-form.html', **locals())

@app.route("/faculty-bio/edit/<faculty_bio_id>")
def faculty_bio_edit_form(faculty_bio_id):

    ##import this here so we dont load all the content
    ##from cascade during homepage load
    from forms import FacultyBioForm

    username = get_user()

    form = FacultyBioForm()

    ################################################################################
    ## Otherwise, pull in the data.
    ################################################################################

    #Get the event data from cascade
    faculty_data = read(faculty_bio_id)

    #Get the different data sets from the response

    form_data = faculty_data.asset.page
    #the stuff from the data def
    s_data = form_data.structuredData.structuredDataNodes.structuredDataNode
    #regular metadata
    metadata = form_data.metadata
    #dynamic metadata
    dynamic_fields = metadata.dynamicFields.dynamicField
    #This dict will populate our EventForm object
    edit_data = {}

    job_titles = {}
    job_title_count = 0


    degrees = {}
    degree_count = 0

    #Start with structuredDataNodes (data def content)
    for node in s_data:
        node_identifier = node.identifier.replace('-', '_')
        node_type = node.type
        if node_type == "text":
            if node_identifier == "job_title":
                job_title_data = node.text
                job_titles[job_title_count] = job_title_data
                job_title_count += 1
            edit_data[node_identifier] = node.text

        elif node_type == 'group':
            if node_identifier == "add_to_bio" or node_identifier == "expertise":
                for group_node in node.structuredDataNodes.structuredDataNode:
                    group_node_identifier = group_node.identifier.replace('-', '_')
                    edit_data[group_node_identifier] = group_node.text
            if node_identifier == "add_degree":
                degree_data = {}
                for degree in node.structuredDataNodes.structuredDataNode:
                    degree_identifier = degree.identifier.replace('-', '_')
                    degree_data[degree.identifier] = degree.text
                    degrees[degree_count] = degree_data
                degree_count += 1

    #now metadata dynamic fields
    for field in dynamic_fields:
        #This will fail if no metadata is set. It should be required but just in case
        if field.fieldValues:
            items = [item.value for item in field.fieldValues.fieldValue]
            edit_data[field.name.replace('-', '_')] = items

    ## Add the rest of the fields. Can't loop over these kinds of metadata
    edit_data['title'] = metadata.title

    #Create an EventForm object with our data
    form = FacultyBioForm(**edit_data)
    form.faculty_bio_id = faculty_bio_id

    #convert job titles and degrees to json so we can use Javascript to create custom DateTime fields on the form
    job_titles = fjson.dumps(job_titles)
    degrees = fjson.dumps(degrees)


    return render_template('faculty-bio-form.html', **locals())

@app.route("/faculty-bio/submit", methods=['POST'])
def submit_faculty_bio_form():

    ##import this here so we dont load all the content
    ##from cascade during hoempage load
    from forms import FacultyBioForm

    username = get_user()
    form = FacultyBioForm()
    rform = request.form

    ## This will need to be done for Job Titles and Expertise.

    # #create a dict of date values so we can access them in Jinja later.
    # #they aren't part of the form so we can't just do form.start1, etc...
    # event_dates, dates_good, num_dates = check_event_dates(rform)
    #
    # dates = []

    # if not form.validate_on_submit() or not dates_good:
    #     if 'event_id' in request.form.keys():
    #         event_id = request.form['event_id']
    #     else:
    #         #This error came from the add form because event_id wasn't set
    #         add_form = True
    #     return render_template('event-form.html', **locals())

    form = rform

    #Get all the form data
    add_data = get_add_data(['school', 'department'], form)
    expertise = get_expertise(add_data)
    add_a_degree = get_add_a_degree(add_data)
    add_to_bio = get_add_to_bio(add_data)

    add_data['expertise'] = expertise
    add_data['add-degree'] = add_a_degree
    add_data['add-to-bio'] = add_to_bio

    username = get_user()

    faculty_bio_id = form['faculty_bio_id']

    asset = get_faculty_bio_structure(add_data, username, faculty_bio_id)

    if faculty_bio_id:
        resp = edit(asset)
        app.logger.warn(time.strftime("%c") + ": event edit submission " + str(resp))
    else:
        resp = create_faculty_bio(asset)
        app.logger.warn(time.strftime("%c") + ": new faculty bio submission " + str(resp) + " MORE: " + asset['page']['id'])



    return redirect('/faculty-bio/confirm', code=302)
    ##Just print the response for now

@app.route('/faculty-bio/confirm')
def faculty_bio_confirm():
    return render_template('/confirm/faculty-bio-confirm.html', **locals())

@app.route('/faculty-bio/delete/<page_id>')
def delete_faculty_bio_page(page_id):
    delete(page_id)
    return redirect('/', 302)