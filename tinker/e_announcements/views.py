# python
from feedformatter import Feed
from urlparse import *
import calendar
import multiprocessing as mp
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


@e_announcements_blueprint.route("/rss_feed", methods=['get', 'post'])
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
    current_url = urlparse(request.url)
    parameters = parse_qs(current_url.query)
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
        print match
        banner_roles = match['roles']
        date_matches = False


        if match['first_date']:
            first_date = datetime.datetime.strptime(match['first_date'], "%A %B %d, %Y")
            if str(datetime.datetime.strptime(date, "%m-%d-%Y")) == str(first_date):
                date_matches = True

        if match['second_date']:
            second_date = datetime.datetime.strptime(match['second_date'], "%A %B %d, %Y")
            if str(datetime.datetime.strptime(date, "%m-%d-%Y")) == str(second_date):
                date_matches = True

        if not date_matches:
            continue

        print first_date

        # if no roles are specified, then display ALL e-announcements that match the day.
        if roles == {}:
            new_matches.append(match)

            # Create an item
            item = {}
            item["title"] = match['title']
            item["link"] = "https://www.bethel.edu/" + match['path']
            item["description"] = '<p>' + match['message'] + "</p><p>(" + ",".join(banner_roles) + ")</p>"
            item["guid"] = "https://www.bethel.edu/" + match['path']
            item['roles'] = 'test'
            rssfeed.items.append(item)
        else:
            break_from_loop = False
            for role in roles:
                for banner_role in banner_roles:
                    if role == banner_role:
                        new_matches.append(match)

                        # Create an item
                        item = {}
                        item["title"] = match['title']
                        item["link"] = "https://www.bethel.edu/" + match['path']
                        item["description"] = '<p>' + match['message'] + "</p><p>(" + ",".join(banner_roles) + ")</p>"
                        item["guid"] = "https://www.bethel.edu/" + match['path']

                        rssfeed.items.append(item)

                        break_from_loop = True
                        break
                if break_from_loop:
                    break

    return Response(rssfeed.format_rss2_string(), mimetype='text/xml')


@e_announcements_blueprint.route("/create_campaign", methods=['get', 'post'])
def create_campaign():
    from itertools import combinations

    # create the necessary IF statement
    # For each for those, make a call to get the announcements for today with those roles
    # Finish the If statement


    output = mp.Queue()

    url = 'http://wsapi.bethel.edu/e-announcement/roles'
    data = urllib2.urlopen(url)
    response = json.load(data)['roles']

    roles = []
    for i in range(1,1000):
        try:
            roles.append( str(response[str(i)]['']) )
        except:
            break

    e_announcements = ''
    count = 1
    e_announcement_array = []

    manager = mp.Manager()
    return_e_announcement_array = manager.dict()

    for role_combo in roles:
        # feedparser.parse(urllib2.urlopen('http://127.0.0.1:5000//e-announcement/rss_feed?date=08-12-2015').read())
        e_announcements += create_single_announcement(role_combo, count)

        p = mp.Process(target=create_single_announcement, args=(role_combo, count, return_e_announcement_array))
        e_announcement_array.append(p)
        p.start()

        count = count + 1

    e_announcements += '[endif]'

    for j in e_announcement_array:
        j.join()

    return str(return_e_announcement_array.values())


    # double check names and ID's and such
    # Finally, append e_announcements to the multiline below. Done.


    # CAMPAIGN_MONITOR_KEY = app.config['CAMPAIGN_MONITOR_KEY']
    # CreateSend({'api_key': CAMPAIGN_MONITOR_KEY})
    #
    # new_campaign = Campaign()
    # new_campaign.auth_details = {}
    # new_campaign.auth_details['api_key'] = CAMPAIGN_MONITOR_KEY
    #
    # client_id = app.config['CLIENT_ID']
    # subject = 'Test Subject'
    # name = 'Test Name'
    # from_name = 'Caleb Testing Campaign'
    # from_email = 'c-schwarze@bethel.edu'
    # reply_to = 'c-schwarze@bethel.edu'
    # list_ids = [app.config['LIST_KEY']]
    # segment_ids = [app.config['SEGMENT_ID']]
    # template_id = app.config['TEMPLATE_ID']
    # template_content = {'Multilines': [{"Content": "[if:TestRoles=FACULTY_CAS;STUDENT_CAPS]<h1>TESTING</h1>[else]<h4>Else</h4>[endif]"}]}
    #
    #
    # resp = new_campaign.create_from_template(client_id, subject, name, from_name, from_email, reply_to, list_ids,
    #                                          segment_ids, template_id, template_content)
    #
    # # resp = new_campaign.create(client_id, subject, name, from_name, from_email, reply_to, "http://www.google.com",
    # #                                          None, list_ids, segment_ids)
    #
    # return str(resp)

@e_announcements_blueprint.route("/create_segment", methods=['get', 'post'])
def create_segment():
    CAMPAIGN_MONITOR_KEY = app.config['CAMPAIGN_MONITOR_KEY']
    CreateSend({'api_key': CAMPAIGN_MONITOR_KEY})

    new_segment = Segment()
    new_segment.auth_details = {}
    new_segment.auth_details['api_key'] = CAMPAIGN_MONITOR_KEY

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


def create_single_announcement(role_combo, count, return_e_announcement_array):

    if count == 1:
        e_announcement = '[if:roles=%s]' % role_combo
    else:
        e_announcement = '[elseif:roles=%s]' % role_combo

    # todo, update the date to be today (aka, remove it)
    for item in feedparser.parse(urllib2.urlopen('http://127.0.0.1:5000//e-announcement/rss_feed?date=08-12-2015&roles=' + role_combo).read())['entries']:
        e_announcement += item['summary_detail']['value']
    return_e_announcement_array[count] = e_announcement
