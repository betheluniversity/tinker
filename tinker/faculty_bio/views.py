# python
import json

from werkzeug.utils import secure_filename

# flask
from flask import Blueprint
from flask import redirect
from flask import send_from_directory
from tinker.sync.metadata import data_to_add

from tinker.faculty_bio.cascade_faculty_bio import *
from tinker import app
from tinker.tools import *

faculty_bio_blueprint = Blueprint('faculty-bio', __name__, template_folder='templates')

@faculty_bio_blueprint.route("/")
def faculty_bio_home():
    username = session['username']
    # index page for adding events and things
    forms = get_faculty_bios_for_user(username)

    show_create = len(forms) == 0 or 'Tinker Faculty Bios' in session['groups']

    # return forms
    return render_template('faculty-bio-home.html', **locals())


@faculty_bio_blueprint.route('/delete/<page_id>')
def delete_page(page_id):
    # send to this workflow instead: 7747ea478c5865130c130b3a1a05240e
    delete(page_id, workflow="7747ea478c5865130c130b3a1a05240e")

    return redirect('/faculty-bio/delete-confirm', code=302)


@faculty_bio_blueprint.route('/delete-confirm')
def delete_confirm():
    return render_template('faculty-bio-delete-confirm.html', **locals())


@faculty_bio_blueprint.route("/edit/new")
def faculty_bio_new_form():
    # import this here so we dont load all the content
    # from cascade during homepage load
    from forms import FacultyBioForm

    form = FacultyBioForm()

    faculty_bio_id = ""

    metadata = fjson.dumps(data_to_add)

    add_form = True
    return render_template('faculty-bio-form.html', **locals())


@faculty_bio_blueprint.route('/confirm-new')
def submit_confirm_new():
    return render_template('faculty-bio-confirm-new.html', **locals())

@faculty_bio_blueprint.route('/confirm-edit')
def submit_confirm_edit():
    return render_template('faculty-bio-confirm-edit.html', **locals())


@faculty_bio_blueprint.route('/in-workflow')
def faculty_bio_in_workflow():
    return render_template('faculty-bio-in-workflow.html')


@faculty_bio_blueprint.route("/edit/<faculty_bio_id>")
def faculty_bio_edit_form(faculty_bio_id):

    # if the event is in a workflow currently, don't allow them to edit. Instead, redirect them.
    if is_asset_in_workflow(faculty_bio_id):
        return redirect('/faculty-bio/in-workflow', code=302)

    # import this here so we dont load all the content
    # from cascade during homepage load
    from forms import FacultyBioForm

    form = FacultyBioForm()

    # Get the event data from cascade
    faculty_data = read(faculty_bio_id)

    form_data = faculty_data.asset.page
    # the stuff from the data def
    s_data = form_data.structuredData.structuredDataNodes.structuredDataNode
    # regular metadata
    metadata = form_data.metadata
    # dynamic metadata
    dynamic_fields = metadata.dynamicFields.dynamicField
    # This dict will populate our EventForm object
    edit_data = {}

    degrees = {}
    degree_count = 0

    new_job_titles = {}
    new_job_title_count = 0

    # Start with structuredDataNodes (data def content)
    # todo rewrite this so each for loop isn't using 'node'
    for node in s_data:
        node_identifier = node.identifier.replace('-', '_')
        node_type = node.type
        if node_type == "text":
            edit_data[node_identifier] = node.text

        elif node_type == 'group':
            if node_identifier == "add_to_bio" or node_identifier == "expertise":
                for group_node in node.structuredDataNodes.structuredDataNode:
                    group_node_identifier = group_node.identifier.replace('-', '_')
                    edit_data[group_node_identifier] = group_node.text
            if node_identifier == "education":
                for node in node.structuredDataNodes.structuredDataNode:
                    node_identifier = node.identifier.replace('-', '_')
                    if node_identifier == "add_degree":
                        degree_data = {}
                        for degree in node.structuredDataNodes.structuredDataNode:
                            degree_identifier = degree.identifier.replace('-', '_')
                            degree_data[degree.identifier] = degree.text
                        degrees[degree_count] = degree_data
                        degree_count += 1
            if node_identifier == "job_titles":
                new_job_title_data = {}
                for field in node.structuredDataNodes.structuredDataNode:
                    node_identifier = field.identifier.replace('-', '_')
                    new_job_title_data[node_identifier] = field.text
                new_job_titles[new_job_title_count] = new_job_title_data
                new_job_title_count += 1

        elif node_identifier == 'image':
            groups = get_groups_for_user()
            edit_data['image'] = node.text
            edit_data['image_url'] = node.filePath

    # now metadata dynamic fields
    for field in dynamic_fields:
        # This will fail if no metadata is set. It should be required but just in case
        if field.fieldValues:
            items = [item.value for item in field.fieldValues.fieldValue]
            edit_data[field.name.replace('-', '_')] = items

    # Add the rest of the fields. Can't loop over these kinds of metadata
    authors = metadata.author
    try:
        authors = authors.split(", ")
        edit_data['author'] = authors[0]
    except AttributeError:
        edit_data['author'] = ''

    # Create an EventForm object with our data
    form = FacultyBioForm(**edit_data)
    form.faculty_bio_id = faculty_bio_id

    # convert job titles and degrees to json so we can use Javascript to create custom DateTime fields on the form
    new_job_titles = fjson.dumps(new_job_titles)
    degrees = fjson.dumps(degrees)

    # metadata for job titles
    metadata = fjson.dumps(data_to_add)

    return render_template('faculty-bio-form.html', **locals())


@faculty_bio_blueprint.route("/submit", methods=['POST'])
def submit_faculty_bio_form():
    # import this here so we dont load all the content
    # from cascade during homepage load
    from forms import FacultyBioForm
    form = FacultyBioForm()

    rform = request.form
    username = session['username']

    title = rform['last'] + "-" + rform['first']
    title = title.lower().replace(' ', '-')
    title = re.sub(r'[^a-zA-Z0-9-]', '', title)

    degrees, degrees_good, num_degrees = check_degrees(rform)
    new_jobs_good, num_new_jobs = check_job_titles(rform)

    if not form.validate_on_submit() or (not new_jobs_good or not degrees_good):
        if 'faculty_bio_id' in request.form.keys():
            faculty_bio_id = request.form['faculty_bio_id']
        else:
            # This error came from the add form because event_id wasn't set
            add_form = True

        metadata = fjson.dumps(data_to_add)
        return render_template('faculty-bio-form.html', **locals())

    # Get all the form data
    add_data = get_add_data(['school', 'department', 'adult_undergrad_program', 'graduate_program', 'seminary_program'], rform)

    # Images
    groups = get_groups_for_user()

    try:
        image_name = form.image.data.filename
    except AttributeError:
        image_name = ""
    if image_name != "":
        image_name = add_data['system_name'] + '.jpg'
        image_path = secure_filename(image_name)


        form.image.data.save(app.config['UPLOAD_FOLDER'] + image_path)

        add_data['image_name'] = image_name
        add_data['image_path'] = image_path

    # End Images

    faculty_bio_id = rform['faculty_bio_id']
    if faculty_bio_id == "":
        faculty_bio_id = None

    workflow = None
    workflow = get_bio_publish_workflow(title, username, faculty_bio_id, add_data['schools1'])
    asset = get_faculty_bio_structure(add_data, username, faculty_bio_id, workflow=workflow)

    if faculty_bio_id:
        # existing bio
        resp = edit(asset)
        app.logger.warn(time.strftime("%c") + ": Faculty bio edit submission by " + username + " with id: " + faculty_bio_id + " " + str(resp))
        # publish corresponding pubish set to make sure corresponding pages get edits
        # This is no longer needed, since ALL bios go through workflows.
        # check_publish_sets(add_data['school'], faculty_bio_id, False)
        return render_template('faculty-bio-confirm-edit.html', **locals())
    else:
        # new bio
        resp = create_faculty_bio(asset)
        faculty_bio_id = resp.createdAssetId
        return render_template('faculty-bio-confirm-new.html', **locals())


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    # return send_from_directory("/Users/ces55739/Sites/Tinker/tinker/temp/images",filename)


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

    # convert event dates to JSON
    return json.dumps(degrees), degrees_good, num_degrees


def check_job_titles(form):
    new_jobs = {}
    new_jobs_good = False

    num_new_jobs = int(form['num_new_jobs'])

    for x in range(1, num_new_jobs+1):  # the page doesn't use 0-based indexing

        i = str(x)
        school_l = 'schools' + i
        undergrad_l = 'undergrad' + i
        caps_l = 'adult-undergrad' + i
        gs_l = 'graduate' + i
        seminary_l = 'seminary' + i
        dept_chair_l = 'dept-chair' + i
        program_director_l = 'program-director' + i
        lead_faculty_l = 'lead-faculty' + i
        job_title_l = 'new-job-title' + i

        ## Todo: clean this up and put it in a nice function.

        try:
            school = form[school_l]
        except:
            school = False
        try:
            undergrad = form[undergrad_l]
            if undergrad is not 'None':
                undergrad = True
        except:
            undergrad = False
        try:
            caps = form[caps_l]
            if caps is not 'None':
                caps = True
        except:
            caps = False
        try:
            gs = form[gs_l]
            if gs is not 'None':
                gs = True
        except:
            gs = False
        try:
            seminary = form[seminary_l]
            if seminary is not 'None':
                seminary = True
        except:
            seminary = False
        try:
            dept_chair = form[dept_chair_l]
            dept_chair = True
        except:
            dept_chair = False
        try:
            program_director = form[program_director_l]
            program_director = True
        except:
            program_director = False
        try:
            lead_faculty = form[lead_faculty_l]
            lead_faculty = True
        except:
            lead_faculty = False
        try:
            job_title = form[job_title_l]
            if job_title != '':
                job_title = True
        except:
            job_title = False

        check = (school == 'Bethel University' and job_title) or ((undergrad or caps or gs or seminary) and (dept_chair or program_director or lead_faculty))
        if check:
            new_jobs_good = True

    # convert event dates to JSON
    return new_jobs_good, num_new_jobs
