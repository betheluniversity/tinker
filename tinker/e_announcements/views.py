# python
from feedformatter import Feed
from urlparse import *
import calendar
import json
import urllib2
import feedparser

# flask
from flask import Blueprint
from flask import redirect
from flask import Response

# tinker
from tinker.e_announcements.cascade_e_announcements import *
from tinker.tools import *

from createsend import *

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
    # import this here so we dont load all the content
    # from cascade during homepage load
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

    # Add the rest of the fields. Can't loop over these kinds of metadata
    edit_data['title'] = metadata.title

    # Create an EventForm object with our data
    form = EAnnouncementsForm(**edit_data)
    form.e_announcement_id = e_announcement_id

    # convert dates to json so we can use Javascript to create custom DateTime fields on the form
    dates = fjson.dumps(dates)

    return render_template('e-announcements-form.html', **locals())


@e_announcements_blueprint.route("/submit", methods=['POST'])
def submit_e_announcement_form():
    # import this here so we dont load all the content
    # from cascade during homepage load
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


@e_announcements_blueprint.route("/submit-edit", methods=['post'])
def submit_edit_form():
    # import this here so we dont load all the content
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
    app.logger.warn(time.strftime("%c") + ": E-Announcement edit submission by " + username + " " + str(resp) + " " + ('id:' + e_announcement_id))

    resp = publish(e_announcement_id, 'page')
    app.logger.warn(time.strftime("%c") + ": E-Announcement publish from " + username + " " + str(resp) + " " + ('id:' + e_announcement_id))

    return redirect('/e-announcement/confirm/edit', code=302)

# Todo: add some kind of authentication?
@e_announcements_blueprint.route("/create_campaign/", methods=['get', 'post'])
@e_announcements_blueprint.route("/create_campaign/<date>", methods=['get', 'post'])
def create_campaign(date=None):
    if not date:
        date = datetime.datetime.now().strftime("%m-%d-%Y")

    # Todo: remove current test default.
    date = datetime.datetime.strptime('Dec 18 2015', '%b %d %Y')

    submitted_announcements = ''
    for announcement in get_e_announcements_for_user():
        date_matches = False

        if announcement['first_date']:
            first_date = datetime.datetime.strptime(announcement['first_date'], "%A %B %d, %Y")
            if str(date) == str(first_date):
                date_matches = True

        if announcement['second_date']:
            second_date = datetime.datetime.strptime(announcement['second_date'], "%A %B %d, %Y")
            if str(date) == str(second_date):
                date_matches = True

        if not date_matches:
            continue

        submitted_announcements += create_single_announcement(announcement)

    campaign_monitor_key = app.config['CAMPAIGN_MONITOR_KEY']
    CreateSend({'api_key': campaign_monitor_key})

    new_campaign = Campaign()
    new_campaign.auth_details = {'api_key': campaign_monitor_key}

    client_id = app.config['CLIENT_ID']
    subject = 'Bethel E-Announcements for ' + str(date.strftime('%A, %B %d, %Y'))
    name = 'Bethel E-Announcements for ' + str(date.strftime('%m/%d/%Y'))
    from_name = 'Bethel E-Announcements'
    from_email = 'e-announcements@lists.bethel.edu'
    reply_to = 'e-announcements@lists.bethel.edu'
    list_ids = [app.config['LIST_KEY']]
    segment_ids = [app.config['SEGMENT_ID']]
    template_id = app.config['TEMPLATE_ID']
    template_content = {'Multilines': [{"Content": submitted_announcements}]}

    resp = new_campaign.create_from_template(client_id, subject, name, from_name, from_email, reply_to, list_ids,
                                             segment_ids, template_id, template_content)

    # Todo: send a preview to whoever needs it.
    # Todo: PROD - update the email to send to whoever checks its sent.
    confirmation_email_sent_to = 'ces55739@bethel.edu'
    # Test version, include this for extra tests str(datetime.datetime.now().strftime('%Y-%m-%d')) + ' 06:00'
    new_campaign.send(confirmation_email_sent_to)
    # Todo: PROD version
    # new_campaign.send(confirmation_email_sent_to, str(date.strftime('%Y-%m-%d')) + ' 06:00')

    return str(resp)

@e_announcements_blueprint.route("/create_segment", methods=['get', 'post'])
def create_segment():
    campaign_monitor_key = app.config['CAMPAIGN_MONITOR_KEY']
    CreateSend({'api_key': campaign_monitor_key})

    new_segment = Segment()
    new_segment.auth_details = {}
    new_segment.auth_details['api_key'] = campaign_monitor_key

    list_id = app.config['LIST_KEY']
    title = 'New Test Segment'
    ruleset = [
        {
            "Rules": [
                {
                    "RuleType": "EmailAddress",
                    "Clause": "CONTAINS @bethel.edu"
                }
            ]
        }
    ]

    resp = new_segment.create(list_id, title, ruleset)
    return str(resp)
