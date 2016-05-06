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
from flask import session
from flask import request

# tinker
from tinker import sentry
from tinker.e_announcements.cascade_e_announcements import *
from tinker.e_announcements.banner_roles_mapping import get_banner_roles_mapping
from tinker.tools import *

# createsend
from createsend import *

e_announcements_blueprint = Blueprint('e-announcement', __name__, template_folder='templates')


@e_announcements_blueprint.route("/")
def e_announcements_home():
    forms = []
    username = session['username']

    # Todo: change this username to be the E-Announcement group
    if username == 'cerntson':
        forms = get_e_announcements_for_user('get_all')
    else:
        forms = get_e_announcements_for_user(username)

    forms.sort(key=lambda item:item['first_date'], reverse=True)
    forms = reversed(forms)
    return render_template('e-announcements-home.html', **locals())


@e_announcements_blueprint.route('/delete/<block_id>')
def delete_page(block_id):
    delete(block_id, type='block')
    # Todo: move this id into config.py
    publish('861012818c5865130c130b3acbee7343')
    return redirect('/e-announcement/delete-confirm', code=302)


@e_announcements_blueprint.route('/delete-confirm')
def delete_confirm():
    return render_template('e-announcements-delete-confirm.html', **locals())


@e_announcements_blueprint.route('/edit/confirm')
def e_announcements_submit_confirm_edit():
    return render_template('e-announcements-confirm-edit.html', **locals())


@e_announcements_blueprint.route('/new/confirm')
def e_announcements_submit_confirm_new():
    return render_template('e-announcements-confirm-new.html', **locals())


@e_announcements_blueprint.route("/new")
def e_announcements_new_form():
    # import this here so we dont load all the content
    # from cascade during homepage load
    from forms import EAnnouncementsForm

    form = EAnnouncementsForm()
    new_form = True

    # bring in the mapping
    banner_roles_mapping = get_banner_roles_mapping()

    return render_template('e-announcements-form.html', **locals())


@e_announcements_blueprint.route('/in-workflow')
def e_announcement_in_workflow():
    return render_template('e-announcements-in-workflow.html')


@e_announcements_blueprint.route('/edit/<e_announcement_id>')
def edit_e_announcement(e_announcement_id):
    if is_asset_in_workflow(e_announcement_id, type='block'):
        return redirect('/e-announcement/in-workflow', code=302)

    from tinker.e_announcements.forms import EAnnouncementsForm

    # Get the event data from cascade
    e_announcement_data = read(e_announcement_id, type='block')
    new_form = False

    # Get the different data sets from the response
    form_data = e_announcement_data.asset.xhtmlDataDefinitionBlock

    # the stuff from the data def
    s_data = form_data.structuredData.structuredDataNodes.structuredDataNode
    # regular metadata
    metadata = form_data.metadata
    # dynamic metadata
    dynamic_fields = metadata.dynamicFields.dynamicField
    # This dict will populate our EventForm object
    dates, edit_data = get_announcement_data(dynamic_fields, metadata, s_data)  # Create an EventForm object with our data
    form = EAnnouncementsForm(**edit_data)
    form.e_announcement_id = e_announcement_id

    # convert dates to json so we can use Javascript to create custom DateTime fields on the form
    dates = fjson.dumps(dates)

    # bring in the mapping
    banner_roles_mapping = get_banner_roles_mapping()

    return render_template('e-announcements-form.html', **locals())


def get_announcement_data(dynamic_fields, metadata, s_data):
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
    today = datetime.datetime.now()
    first_readonlye = False
    second_readonly = False
    if edit_data['first'] < today:
        first_readonly = edit_data['first'].strftime('%A %B %d, %Y')
    if edit_data['second'] and edit_data['second'] < today:
        second_readonly = edit_data['second'].strftime('%A %B %d, %Y')

    # A fix to remove the &#160; character from appearing (non-breaking whitespace)
    # Cascade includes this, for whatever reason.
    edit_data['message'] = edit_data['message'].replace('&amp;#160;', ' ')

    return dates, edit_data


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

        app.logger.debug(time.strftime("%c") + ": E-Announcement submission failed by  " + username + ". Submission could not be validated")

        # bring in the mapping
        banner_roles_mapping = get_banner_roles_mapping()

        return render_template('e-announcements-form.html', **locals())

    # Get all the form data
    add_data = get_add_data(['banner_roles'], rform)
    if 'e_announcement_id' in rform:
        e_announcement_id = rform['e_announcement_id']
    else:
        e_announcement_id = None

    workflow = get_e_announcement_publish_workflow(title)
    asset = get_e_announcement_structure(add_data, username, workflow=workflow, e_announcement_id=e_announcement_id)

    if e_announcement_id:
        resp = edit(asset)
        log_sentry("E-Announcement edit submission", resp)
        return redirect('/e-announcement/edit/confirm', code=302)
    else:
        resp = create_e_announcement(asset)

    log_sentry('New e-announcement submission', resp)

    return redirect('/e-announcement/new/confirm', code=302)


@e_announcements_blueprint.route('/view/<block_id>')
def view_announcement(block_id):
    e_announcement_data = read(block_id, type='block')

    # Get the different data sets from the response
    form_data = e_announcement_data.asset.xhtmlDataDefinitionBlock

    # the stuff from the data def
    s_data = form_data.structuredData.structuredDataNodes.structuredDataNode
    # regular metadata
    metadata = form_data.metadata
    # dynamic metadata
    dynamic_fields = metadata.dynamicFields.dynamicField

    dates, edit_data = get_announcement_data(dynamic_fields, metadata, s_data)

    first = dates[0].strftime('%A %B %d, %Y')

    if len(dates) > 1:
        second = dates[1].strftime('%A %B %d, %Y')

    return render_template('e-announcements-view.html', **locals())


@e_announcements_blueprint.route("/create_and_send_campaign/", methods=['get', 'post'])
@e_announcements_blueprint.route("/create_campaign/", methods=['get', 'post'])
@e_announcements_blueprint.route("/create_campaign/<date>", methods=['get', 'post'])
@requires_auth
def create_campaign(date=None):
    if not date:
        date = datetime.datetime.strptime(datetime.datetime.now().strftime("%m-%d-%Y"), "%m-%d-%Y")
    else:
        date = datetime.datetime.strptime(date, "%m-%d-%Y")

    if not check_if_valid_date(date):
        return 'E-Announcements are not set to run today. No campaign was created and no E-Announcements were sent out.'

    submitted_announcements = []
    current_announcement_role_list = []
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

        # add announcement
        submitted_announcements.append({
            "Layout":
                "announcements",
                "Multilines": [
                    {
                        "Content": create_single_announcement(announcement)
                    }
                ]
            }
        )

        # create a list of all roles that are currently receiving E-Announcements
        for role in announcement['roles']:
            if role not in current_announcement_role_list:
                current_announcement_role_list.append(role)

    campaign_monitor_key = app.config['CAMPAIGN_MONITOR_KEY']
    CreateSend({'api_key': campaign_monitor_key})
    new_campaign = Campaign({'api_key': campaign_monitor_key})

    client_id = app.config['CLIENT_ID']
    subject = 'Bethel E-Announcements | ' + str(date.strftime('%A, %B %-d, %Y'))
    name = 'Bethel E-Announcements | ' + str(date.strftime('%m/%-d/%Y'))
    from_name = 'Bethel E-Announcements'
    from_email = 'e-announcements@lists.bethel.edu'
    reply_to = 'e-announcements@lists.bethel.edu'
    list_ids = [app.config['LIST_KEY']]
    segment_ids = [app.config['SEGMENT_ID']]
    template_id = app.config['TEMPLATE_ID']
    template_content = {
        "Singlelines": [
            {
                "Content": 'Bethel E-Announcements<br/>' + str(date.strftime('%A, %B %-d, %Y')),
            },
            {
                "Content": '<a href="https://www.bethel.edu/e-announcements/archive?date=%s">View all E-Announcements for today.</a>' % str(date.strftime('%m-%d-%Y'))
            }
        ],
        "Multilines": [
            {
                "Content": get_layout_for_no_announcements(current_announcement_role_list),
            }
        ],
        "Repeaters": [
            {
                "Items": submitted_announcements
            },
        ]
    }

    # Todo: if a campaign already exists, delete the old one and create a new one
    resp = new_campaign.create_from_template(client_id, subject, name, from_name, from_email, reply_to, list_ids,
                                         segment_ids, template_id, template_content)

    if 'create_and_send_campaign' in request.url_rule.rule and app.config['ENVIRON'] == 'prod':
        # Send the announcements out to ALL users at 7:00 am.
        confirmation_email_sent_to = ', '.join(app.config['ADMINS'])
        new_campaign.send(confirmation_email_sent_to, str(date.strftime('%Y-%m-%d')) + ' 06:30')

        # if we ever want to send an e-announcement immediately, here it is.
        # WARNING: be careful about accidentally sending emails to mass people.
        # new_campaign.send(confirmation_email_sent_to)

    return str(resp)
