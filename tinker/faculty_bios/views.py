#python
import json

#flask
from flask import Blueprint
from flask import render_template
from flask import redirect

from tinker.faculty_bios.cascade_faculty_bio import *
from tinker import app
from tinker import tools

faculty_bio_blueprint = Blueprint('faculty-bios', __name__,
                        template_folder='templates')

@faculty_bio_blueprint.route("/")
def faculty_bio_home():
    ## index page for adding events and things
    username = tools.get_user()

    forms = get_faculty_bios_for_user(username)
    # return forms
    return render_template('faculty-bio-home.html', **locals())

@faculty_bio_blueprint.route('/delete/<page_id>')
def delete_page(page_id):
    delete(page_id)
    return redirect('/faculty-bios/delete-confirm', code=302)

@faculty_bio_blueprint.route('/delete-confirm')
def delete_confirm():
    return render_template('delete-confirm.html', **locals())

@faculty_bio_blueprint.route("/edit/new")
def faculty_bio_new_form():
    ##import this here so we dont load all the content
    ##from cascade during homepage load
    from forms import FacultyBioForm

    username = tools.get_user()

    form = FacultyBioForm()

    add_form = True
    return render_template('faculty-bio-form.html', **locals())

@faculty_bio_blueprint.route('/confirm')
def submit_confirm():
    return render_template('faculty-bio-confirm.html', **locals())

@faculty_bio_blueprint.route("/edit/<faculty_bio_id>")
def faculty_bio_edit_form(faculty_bio_id):

    ##import this here so we dont load all the content
    ##from cascade during homepage load
    from forms import FacultyBioForm

    username = tools.get_user()

    form = FacultyBioForm()

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
            if node_identifier == "education":
                node = node.structuredDataNodes.structuredDataNode[0]
                node_identifier = node.identifier.replace('-', '_')
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


    ## only take the first element
    authors = metadata.author
    authors = authors.split(", ")
    edit_data['author'] = authors[0]

    #Create an EventForm object with our data
    form = FacultyBioForm(**edit_data)
    form.faculty_bio_id = faculty_bio_id

    #convert job titles and degrees to json so we can use Javascript to create custom DateTime fields on the form
    job_titles = fjson.dumps(job_titles)
    degrees = fjson.dumps(degrees)

    return render_template('faculty-bio-form.html', **locals())


@faculty_bio_blueprint.route("/submit", methods=['POST'])
def submit_faculty_bio_form():

    ##import this here so we dont load all the content
    ##from cascade during hoempage load
    from forms import FacultyBioForm

    username = tools.get_user()
    form = FacultyBioForm()
    rform = request.form
    title = rform['title']
    workflow = get_bio_publish_workflow(title, username)

    jobs, jobs_good, num_jobs = check_jobs(rform)
    degrees, degrees_good, num_degrees = check_degrees(rform)

    if not form.validate_on_submit() or not jobs_good:
        if 'faculty_bio_id' in request.form.keys():
            faculty_bio_id = request.form['faculty_bio_id']
        else:
            #This error came from the add form because event_id wasn't set
            add_form = True
        return render_template('faculty-bio-form.html', **locals())



    form = rform

    #Get all the form data
    add_data = get_add_data(['school', 'department'], form) ##, 'adult_undergrad_program', 'graduate_program', 'seminary_program'], form)
    # expertise = get_expertise(add_data)
    # add_a_degree = get_add_a_degree(add_data)
    # add_to_bio = get_add_to_bio(add_data)
    #
    # add_data['expertise'] = expertise
    # add_data['add-degree'] = add_a_degree
    # add_data['add-to-bio'] = add_to_bio

    username = tools.get_user()

    faculty_bio_id = form['faculty_bio_id']

    asset = get_faculty_bio_structure(add_data, username, faculty_bio_id, workflow=workflow)



    ## Depending on the type of submit, return a different error message.
    ## ALSO, this can be modified to have separate returned templates (or redirects )
    if faculty_bio_id:
        resp = edit(asset)
        app.logger.warn(time.strftime("%c") + ": Faculty bio edit submission by " + username + " " + str(resp))
        publish(faculty_bio_id)
    else:
        resp = create_faculty_bio(asset)


    return redirect('/faculty-bios/confirm', code=302)
    ##Just print the response for now



def check_jobs(form):
    jobs = {}
    jobs_good = False

    num_jobs = int(form['num_jobs'])

    for x in range(1, num_jobs+1):  # the page doesn't use 0-based indexing

        i = str(x)
        job_l = 'job-title' + i

        job = form[job_l]

        jobs[job_l] = job


        if job:
            jobs_good = True

    #convert event dates to JSON
    return json.dumps(jobs), jobs_good, num_jobs


def check_degrees(form):
    degrees = {}
    degrees_good = False

    num_degrees = int(form['num_degrees'])

    for x in range(1, num_degrees+1):  # the page doesn't use 0-based indexing

        i = str(x)
        school_l = 'school' + i
        degree_earned_l = 'degree-earned' + i
        year_l = 'year' + i

        school = form[school_l]
        degree_earned = form[degree_earned_l]
        year = form[year_l]

        degrees[school_l] = school
        degrees[degree_earned_l] = degree_earned
        degrees[year_l] = year

        check = school and degree_earned and year


        if check:
            degrees_good = True

    #convert event dates to JSON
    return json.dumps(degrees), degrees_good, num_degrees