#python
import datetime
import re
from xml.etree import ElementTree as ET
import urllib2

#flask
from flask import render_template
from flask import request
from flask import redirect
from cascade_web_services import app

#local
from forms import EventForm

from tools import get_client

@app.route('/delete/<page_id>')
def remove_page(page_id):
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

    return render_template('admin.html', **locals())

@app.route("/read")
def read_page():

    return "<pre>" + read_event_index() + "</pre>"


def get_add_data(lists, form):

    ##A dict to populate with all the interesting data.
    add_data = {}

    for key in form.keys():
        if key in lists:
            add_data[key] = form.getlist(key)
        else:
            add_data[key] = form[key]

    ##Create the system-name from title, all lowercase
    system_name = add_data['title'].lower().replace(' ', '-')

    ##Now remove any non a-z, A-Z, 0-9
    system_name = re.sub(r'[^a-zA-Z0-9-]', '', system_name)

    add_data['system_name'] = system_name

    return add_data


def get_dates(add_data):

    dates = []

    ##format the dates
    for i in range(1, 200):
        i = str(i)
        try:
            start = 'start' + i
            end = 'end' + i
            all_day = 'allday' + i

            start = add_data[start]
            end = add_data[end]
            all_day = all_day in add_data.keys()

        except KeyError:
            ##This will break once we run out of dates
            break

        #Get rid of the facy formatting so we just have normal numbers
        start = start.replace('th', '').replace('st', '').replace('rd', '')
        end = end.replace('th', '').replace('st', '').replace('rd', '')

        # Convert to a unix timestamp, and then multiply by 1000 because Cascade uses Java dates
        # which use milliseconds instead of seconds
        try:
            start = int(datetime.datetime.strptime(start, '%B %d  %Y, %I:%M %p').strftime("%s")) * 1000
        except ValueError:
            start = None
        try:
            end = int(datetime.datetime.strptime(end, '%B %d  %Y, %I:%M %p').strftime("%s")) * 1000
        except ValueError:
            end = None

        dates.append(event_date(start, end, all_day))

    return dates

@app.route("/submit", methods=['POST'])
def submit_form():

    form = EventForm()
    if not form.validate_on_submit():
        return render_template('admin.html', form=form)

    form = request.form
    #Get all the form data
    add_data = get_add_data(['general', 'offices', 'academics_dates', 'cas_departments', 'internal'], form)

    dates = get_dates(add_data)

    ##Add it to the dict, we can just ignore the old entries
    add_data['dates'] = dates

    resp = create_new_event(add_data)

    code = re.search('createdAssetId = "(.*?)"', resp).group(1)

    return redirect('/', code=302)
    ##Just print the response for now
    ##return resp


def create_new_event(add_data):
    """
     Could this be cleaned up at all?
    """

    client = get_client()

    ## Create a list of all the data nodes
    structured_data = [
        structured_data_node("main-content", add_data['description']),
        structured_data_node("questions", add_data['questions']),
        structured_data_node("cancellations", add_data['refunds']),
        structured_data_node("registration-details", add_data['details']),
        structured_data_node("registration-heading", add_data['heading']),
        structured_data_node("cost", add_data['cost']),
        structured_data_node("sponsors", add_data['sponsors']),
        structured_data_node("maps-directions", add_data['directions']),
        structured_data_node("off-campus-location", add_data['off_location']),
        structured_data_node("location", add_data['location']),
        structured_data_node("featuring", add_data['featuring']),
        structured_data_node("wufoo-code", add_data['wufoo']),


    ]
    ## Add the dates at the end of the data
    structured_data.extend(add_data['dates'])

    ## Wrap in the required structure for SOAP
    structured_data = {
        'structuredDataNodes': {
            'structuredDataNode': structured_data,
        }
    }

    #create the dynamic metadata dict
    dynamic_fields = {
        'dynamicField': [
            dynamic_field('general', add_data['general']),
            dynamic_field('offices', add_data['offices']),
            dynamic_field('academic-dates', add_data['academics_dates']),
            dynamic_field('cas-departments', add_data['cas_departments']),
            dynamic_field('internal', add_data['internal']),
        ],
    }

    #put it all into the final asset with the rest of the SOAP structure
    asset = {
        'page': {
            'name': add_data['system_name'],
            'siteId': "ba134ac58c586513100ee2a7cec27f4a",
            'parentFolderPath': "testing",
            'metadataSetPath': "/Event",
            'contentTypePath': "/Event",
            'configurationSetPath': "/Event",
            ## Break this out more once its defined in the form
            'structuredData': structured_data,
            'metadata': {
                'title': add_data['title'],
                'summary': 'summary',
                'author': "ejc84332",  # replace this with the CAS user eventually.
                'metaDescription': add_data['teaser'],  # replace this with the CAS user eventually.
                'dynamicFields': dynamic_fields,
            }
        }
    }
    ##Create the Auth list. Need a real username and password eventually
    auth = app.config['CASCADE_LOGIN']

    response = client.service.create(auth, asset)

    ##publish the xml file so the new event shows up
    publish_event_xml()

    return str(response)


def traverse_folder(traverse_xml, username):
    ## Travserse an XML folder, adding system-pages to a dict of matches

    matches = []
    for child in traverse_xml:
        if child.tag == 'system-page':
            try:
                author = child.find('author').text
            except AttributeError:
                continue
            if author == username:
                page_values = {
                    'author': child.find('author').text,
                    'id': child.attrib['id'] or None,
                    'title': child.find('title').text or None,
                    'created-on': child.find('created-on').text or None,
                    'path': 'http://staging.bethel.edu' + child.find('path').text or None,
                }
                ## This is a match, add it to array
                matches.append(page_values)

        elif child.tag is 'system-folder':
            ##recurse into the page
            matches.extend(traverse_folder(child, username))
    return matches


def get_forms_for_user(username):

    response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/events.xml')
    form_xml = ET.fromstring(response.read())
    matches = traverse_folder(form_xml, username)

    return matches


def delete(page_id):

    client = get_client()

    identifier = {
        'id': page_id,
        'type': 'page',
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.delete(auth, identifier)
    ## Publish the XML so the event is gone
    publish_event_xml()
    return response


def dynamic_field(name, values):

    values_list = []
    for value in values:
        values_list.append({'value': value})
    node = {
        'name': name,
        'fieldValues': {
            'fieldValue': values_list,
        },
    },

    return node


def structured_data_node(id, text, node_type=None):

    if not node_type:
        node_type = "text"

    node = {

        'identifier': id,
        'text': text,
        'type': node_type,
    }

    return node


def event_date(start, end, all_day=False):

    list = [
        structured_data_node("start-date", start),
        structured_data_node("end-date", end),
        ]
    if all_day:
        list.append(structured_data_node("all-day", "::CONTENT-XML-CHECKBOX::Yes"))

    node = {
        'type': "group",
        'identifier': "event-dates",
        'structuredDataNodes': {
            'structuredDataNode': list,
        },
    },

    return node

@app.route('/publish')
def publish_event_xml():

    client = get_client()

    publishinformation = {
        'identifier': {
            'id': '4eea96d18c5865135b5a2d9e155b78a9',
            'type': 'page'
        }
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.publish(auth, publishinformation)

    return str(response)