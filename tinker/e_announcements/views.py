#python

#flask
from flask import Blueprint
from flask import redirect

from tinker.e_announcements.cascade_e_announcements import *
from tinker.tools import *

e_announcements_blueprint = Blueprint('e-announcements', __name__, template_folder='templates')


@e_announcements_blueprint.route("/")
def e_announcements_home():
    username = session['username']
    forms = get_e_announcements_for_user(username)
    return render_template('e-announcements-home.html', **locals())


@e_announcements_blueprint.route('/delete/<page_id>')
def delete_page(page_id):
    delete(page_id)
    return redirect('/e-announcements/delete-confirm', code=302)


@e_announcements_blueprint.route('/delete-confirm')
def delete_confirm():
    return render_template('e-announcements-delete-confirm.html', **locals())


@e_announcements_blueprint.route('/confirm')
def e_announcements_submit_confirm():
    return render_template('e-announcements-confirm.html', **locals())


@e_announcements_blueprint.route("/edit/new")
def e_announcements_new_form():
    ##import this here so we dont load all the content
    ##from cascade during homepage load
    from forms import EAnnouncementsForm

    form = EAnnouncementsForm()
    add_form = True
    return render_template('e-announcements-form.html', **locals())


@e_announcements_blueprint.route("/submit", methods=['POST'])
def submit_e_announcement_form():
    ##import this here so we dont load all the content
    ##from cascade during homepage load
    from forms import EAnnouncementsForm
    form = EAnnouncementsForm()
    rform = request.form
    username = session['username']
    title = rform['title']
    title = title.lower().replace(' ', '-')
    title = re.sub(r'[^a-zA-Z0-9-]', '', title)

    workflow = get_e_announcement_publish_workflow(title, username)

    if not form.validate_on_submit():
        if 'e_announcement_id' in request.form.keys():
            e_announcement_id = request.form['e_announcement_id']
        else:
            #This error came from the add form because e-annoucnements_id wasn't set
            add_form = True
        app.logger.warn(time.strftime("%c") + ": E-Announcement submission failed by  " + username + ". Submission could not be validated")
        return render_template('e-announcements-form.html', **locals())

    #Get all the form data
    add_data = get_add_data(['audience'], rform)

    asset = get_e_announcement_structure(add_data, username, workflow=workflow)
    resp = create_e_announcement(asset)
    # publish("f580ac758c58651313b6fe6bced65fea", "publishset")

    return redirect('/e-announcements/confirm', code=302)
    ##Just print the response for now


@e_announcements_blueprint.route('/edit/<e_announcement_id>')
def edit_e_announcement(e_announcement_id):
    from tinker.e_announcements.forms import EAnnouncementsForm

    #Get the event data from cascade
    e_announcement_data = read(e_announcement_id)

    #Get the different data sets from the response

    form_data = e_announcement_data.asset.page

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

        if node_identifier == "first_date":
            node_identifier = "first"
        if node_identifier == "second_date":
            node_identifier = "second"

        node_type = node.type

        if node_type == "text":
            if node_identifier == "first" or node_identifier == "second":
                edit_data[node_identifier] = datetime.datetime.strptime(node.text, "%m-%d-%Y")
            else:
                edit_data[node_identifier] = node.text

    #now metadata dynamic fields
    for field in dynamic_fields:
        #This will fail if no metadata is set. It should be required but just in case
        if field.fieldValues:
            items = [item.value for item in field.fieldValues.fieldValue]
            edit_data[field.name.replace('-', '_')] = items

    ## Add the rest of the fields. Can't loop over these kinds of metadata
    edit_data['title'] = metadata.title

    #Create an EventForm object with our data
    form = EAnnouncementsForm(**edit_data)
    form.e_announcement_id = e_announcement_id

    return render_template('e-announcements-form.html', **locals())


@e_announcements_blueprint.route("/submit-edit", methods=['post'])
def submit_edit_form():

    ##import this here so we dont load all the content
    ##from cascade during hoempage load
    from tinker.e_announcements.forms import EAnnouncementsForm

    form = EAnnouncementsForm()
    rform = request.form
    title = rform['title']
    username = session['username']
    workflow = get_e_announcement_publish_workflow(title, username)

    if not form.validate_on_submit():
        e_announcement_id = request.form['e_announcement_id']
        return render_template('e-announcements-form.html', **locals())

    form = rform
    e_announcement_id = form['e_announcement_id']

    add_data = get_add_data(['audience'], form)
    asset = get_e_announcement_structure(add_data, username, workflow=workflow, e_announcement_id=e_announcement_id)

    resp = edit(asset)
    app.logger.warn(time.strftime("%c") + ": E-Announcement edit submission by " + username + " " + str(resp))

    ## Todo: Make sure to publish the page down the road!

    #return str(resp)
    return redirect('/e-announcements/confirm', code=302)