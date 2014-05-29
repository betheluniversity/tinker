#python
import datetime
import re

#flask
from flask import render_template
from flask import request
from cascade_web_services import app


#local
from forms import EventForm

from tools import get_client


@app.route("/")
def form_index():

    form = EventForm()

    return render_template('admin.html', **locals())

@app.route("/read")
def read_page():

    client = get_client()
    return "<pre>" + readPage(client) + "</pre>"


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
        start = int(datetime.datetime.strptime(start, '%B %d  %Y, %I:%M %p').strftime("%s")) * 1000
        end = int(datetime.datetime.strptime(end, '%B %d  %Y, %I:%M %p').strftime("%s")) * 1000

        dates.append(eventDate(start, end, all_day))

    return dates

@app.route("/submit", methods=['POST'])
def submit_form():

    form = request.form

    #Get all the form data
    add_data = get_add_data(['general', 'academics', 'offices', 'internal'], form)

    dates = get_dates(add_data)

    ##Add it to the dict, we can just ignore the old entries
    add_data['dates'] = dates

    resp = create_new_event(add_data)

    ##Just print the response for now
    return resp


def create_new_event(add_data):
    """
     Could this be cleaned up at all?
    """

    client = get_client()

    ## Create a list of all the data nodes
    structured_data = [
        structuredDataNode("main-content", add_data['description']),
        structuredDataNode("questions", add_data['questions']),
        structuredDataNode("cancellations", add_data['refunds']),
        structuredDataNode("registration-details", add_data['details']),
        structuredDataNode("registration-heading", add_data['heading']),
        structuredDataNode("cost", add_data['cost']),
        structuredDataNode("sponsors", add_data['sponsors']),
        structuredDataNode("maps-directions", add_data['directions']),
        structuredDataNode("off-campus-location", add_data['off_location']),
        structuredDataNode("location", add_data['location']),
        structuredDataNode("featuring", add_data['featuring']),
        structuredDataNode("wufoo-code", add_data['wufoo']),


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
            dynamicField('general', add_data['general']),
            dynamicField('offices', add_data['offices']),
            dynamicField('academics', add_data['academics']),
            dynamicField('internal', add_data['internal']),
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
                'displayName': add_data['title'],
                'summary': 'summary',
                'author': "ejc84332",  # replace this with the CAS user eventually.
                'dynamicFields': dynamic_fields,
            }
        }
    }
    ##Create the Auth list. Need a real username and password eventually
    auth = app.config['CASCADE_LOGIN']

    response = client.service.create(auth, asset)
    return str(response)


def readPage(client):

    auth = app.config['CASCADE_LOGIN']

    identifier = {
        'path': {
            'path': '/testing/test-event',
            'siteName': 'Public'
        },
        'type': 'page',
    }

    response = client.service.read(auth, identifier)
    return str(response)


def dynamicField(name, values):

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


def structuredDataNode(id, text, node_type=None):

    if not node_type:
        node_type = "text"

    node = {

        'identifier': id,
        'text': text,
        'type': node_type,
    }

    return node

def eventDate(start, end, all_day=False):

    list = [
        structuredDataNode("start-date", start),
        structuredDataNode("end-date", end),
        ]
    if all_day:
        list.append(structuredDataNode("all-day", "::CONTENT-XML-CHECKBOX::Yes"))

    node = {
        'type': "group",
        'identifier': "event-dates",
        'structuredDataNodes': {
            'structuredDataNode': list,
        },
    },

    return node


