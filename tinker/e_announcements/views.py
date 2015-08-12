# python
from feedformatter import Feed
import urlparse
import calendar

# flask
from flask import Blueprint
from flask import redirect
from flask import Response

# tinker
from tinker.e_announcements.cascade_e_announcements import *
from tinker.tools import *

e_announcements_blueprint = Blueprint('e-announcement', __name__, template_folder='templates')


# Todo: sort e-announcements by most recent date.
@e_announcements_blueprint.route("/")
def e_announcements_home():
    username = session['username']
    forms = get_e_announcements_for_user(username)
    return render_template('e-announcements-home.html', **locals())


@e_announcements_blueprint.route('/delete/<page_id>')
def delete_page(page_id):
    delete(page_id)
    return redirect('/e-announcement/delete-confirm', code=302)


@e_announcements_blueprint.route('/delete-confirm')
def delete_confirm():
    return render_template('e-announcements-delete-confirm.html', **locals())


@e_announcements_blueprint.route('/confirm/edit')
def e_announcements_submit_confirm_edit():
    return render_template('e-announcements-confirm-edit.html', **locals())


@e_announcements_blueprint.route('/confirm/new')
def e_announcements_submit_confirm_new():
    return render_template('e-announcements-confirm-new.html', **locals())


@e_announcements_blueprint.route("/edit/new")
def e_announcements_new_form():
    ## import this here so we dont load all the content
    ## from cascade during homepage load
    from forms import EAnnouncementsForm

    form = EAnnouncementsForm()
    new_form = True
    return render_template('e-announcements-form.html', **locals())


@e_announcements_blueprint.route('/edit/<e_announcement_id>')
def edit_e_announcement(e_announcement_id):
    from tinker.e_announcements.forms import EAnnouncementsForm

    # Get the event data from cascade
    e_announcement_data = read(e_announcement_id)

    # Get the different data sets from the response

    form_data = e_announcement_data.asset.page

    # the stuff from the data def
    s_data = form_data.structuredData.structuredDataNodes.structuredDataNode
    # regular metadata
    metadata = form_data.metadata
    # dynamic metadata
    dynamic_fields = metadata.dynamicFields.dynamicField
    # This dict will populate our EventForm object
    edit_data = {}
    dates = []

    # Start with structuredDataNodes (data def content)
    for node in s_data:
        node_identifier = node.identifier.replace('-', '_')

        if node_identifier == "first_date":
            node_identifier = "first"
        if node_identifier == "second_date":
            node_identifier = "second"

        node_type = node.type

        if node_type == "text":
            if (node_identifier == "first" or node_identifier == "second") and node.text:
                edit_data[node_identifier] = datetime.datetime.strptime(node.text, "%m-%d-%Y")
                dates.append(datetime.datetime.strptime(node.text, "%m-%d-%Y"))
            else:
                edit_data[node_identifier] = node.text

    # now metadata dynamic fields
    for field in dynamic_fields:
        if field.fieldValues:
            items = [item.value for item in field.fieldValues.fieldValue]
            edit_data[field.name.replace('-', '_')] = items

    ## Add the rest of the fields. Can't loop over these kinds of metadata
    edit_data['title'] = metadata.title

    # Create an EventForm object with our data
    form = EAnnouncementsForm(**edit_data)
    form.e_announcement_id = e_announcement_id

    # convert dates to json so we can use Javascript to create custom DateTime fields on the form
    dates = fjson.dumps(dates)

    return render_template('e-announcements-form.html', **locals())


@e_announcements_blueprint.route("/submit", methods=['POST'])
def submit_e_announcement_form():
    ## import this here so we dont load all the content
    ## from cascade during homepage load
    from forms import EAnnouncementsForm
    form = EAnnouncementsForm()
    rform = request.form
    username = session['username']
    title = rform['title']
    title = title.lower().replace(' ', '-')
    title = re.sub(r'[^a-zA-Z0-9-]', '', title)


    if not form.validate_on_submit():
        if 'e_announcement_id' in request.form.keys():
            e_announcement_id = request.form['e_announcement_id']
        else:
            # This error came from the add form because e-annoucnements_id wasn't set
            new_form = True
        app.logger.warn(time.strftime("%c") + ": E-Announcement submission failed by  " + username + ". Submission could not be validated")
        return render_template('e-announcements-form.html', **locals())

    # Get all the form data
    add_data = get_add_data(['banner_roles'], rform)

    workflow = get_e_announcement_publish_workflow(title, username)
    asset = get_e_announcement_structure(add_data, username, workflow=workflow)
    resp = create_e_announcement(asset)
    # publish("f580ac758c58651313b6fe6bced65fea", "publishset")

    return redirect('/e-announcement/confirm/new', code=302)
    ## Just print the response for now


@e_announcements_blueprint.route("/submit-edit", methods=['post'])
def submit_edit_form():

    ## import this here so we dont load all the content
    ## from cascade during hoempage load
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

    add_data = get_add_data(['banner_roles'], form)
    asset = get_e_announcement_structure(add_data, username, workflow=workflow, e_announcement_id=e_announcement_id)

    resp = edit(asset)
    app.logger.warn(time.strftime("%c") + ": E-Announcement edit submission by " + username + " " + str(resp)+ " " + ('id:' + e_announcement_id))

    ## Todo: Make sure to publish the page down the road!

    # return str(resp)
    return redirect('/e-announcement/confirm/edit', code=302)


@e_announcements_blueprint.route("/rss_feed", methods=['get'])
def rss_feed():
    # Create the feed
    rssfeed = Feed()

    # Set the feed/channel level properties
    rssfeed.feed["title"] = "E-announcements rss feed"
    rssfeed.feed["link"] = "https://www.bethel.edu/_shared-content/xml/e-announcements.xml"
    rssfeed.feed["language"] = "en-us"
    rssfeed.feed["author"] = "Tinker"
    rssfeed.feed["description"] = "E-announcements feed"

    # get url variables
    current_url = urlparse.urlparse(request.url)
    parameters = urlparse.parse_qs(current_url.query)
    if 'roles' in parameters:
        roles = parameters['roles'][0].split('_')
        roles = [role.upper() for role in roles]
    else:
        roles = {}
    if 'date' in parameters:
        try:
            date = parameters['date'][0]
        except ValueError:
            raise ValueError("Incorrect date format. Use MM-DD-YYYY")
    else:
        date = datetime.datetime.now().strftime("%m-%d-%Y")

    ## Get each of the matching e-announcements to put into new_matches
    matches = get_e_announcements_for_user()
    new_matches = []

    ## For each e-announcement
    for match in matches:
        match = read(match['id'])
        if match.success == "false":
            continue
        match = match.asset.page

        ### Gather the information
        metadata = match.metadata
        dynamic_fields = metadata.dynamicFields.dynamicField

        # now metadata dynamic fields
        for field in dynamic_fields:

            # This will fail if no metadata is set. It should be required but just in case
            if field.fieldValues and field.name == "banner-roles":
                banner_roles = [item.value for item in field.fieldValues.fieldValue]

        edit_data = {}
        date_matches = False
        s_data = match.structuredData.structuredDataNodes.structuredDataNode
        for node in s_data:
            node_identifier = node.identifier.replace('-', '_')
            node_type = node.type

            if node_type == "text":
                if node_identifier == "first_date" or (node.text and node_identifier == "second_date"):
                    if str(datetime.datetime.strptime(date, "%m-%d-%Y")) == str(datetime.datetime.strptime(node.text, "%m-%d-%Y")):
                        date_matches = True
                    edit_data[node_identifier] = datetime.datetime.strptime(node.text, "%m-%d-%Y")
                else:
                    edit_data[node_identifier] = node.text

        if not date_matches:
            continue

        ### Use the information
        ## Check if an input role matches a role of the e-announcement
        break_from_loop = False
        for role in roles:
            for banner_role in banner_roles:
                if role == banner_role:
                    new_matches.append(match)

                    # Create an item
                    item = {}
                    item["title"] = match.metadata.title
                    item["link"] = "https://www.bethel.edu/" + match.path
                    item["description"] = edit_data['message'] + " <p>(" + ",".join(banner_roles ) + ")</p>"
                    item["guid"] = "https://www.bethel.edu/" + match.path
                    # item["roles"] = ", ".join([role.upper() for role in roles])
                    if match.lastPublishedDate != None:
                        item["pubDate"] = calendar.timegm(match.lastPublishedDate.utctimetuple())

                    rssfeed.items.append(item)

                    break_from_loop = True
                    break
            if break_from_loop :
                break

        # if no roles are specified, then display ALL e-announcements that match the day.
        if roles == {}:
            new_matches.append(match)

            # Create an item
            item = {}
            item["title"] = match.metadata.title
            item["link"] = "https://www.bethel.edu/" + match.path
            item["description"] = edit_data['message'] + " <p>(" + ",".join(banner_roles ) + ")</p>"
            item["guid"] = "https://www.bethel.edu/" + match.path
            # item["roles"] = ", ".join([role.upper() for role in roles])
            if match.lastPublishedDate != None:
                item["pubDate"] = calendar.timegm(match.lastPublishedDate.utctimetuple())

            rssfeed.items.append(item)

    return Response(rssfeed.format_rss2_string(), mimetype='text/xml')
