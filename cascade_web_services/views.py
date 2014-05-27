#python
import datetime
import time
#flask
from flask import render_template
from flask import request
from cascade_web_services import app

from suds.client import Client

#local
from forms import EventForm


@app.route("/")
def form_index():

    form = EventForm()

    return render_template('admin.html', **locals())

@app.route("/read")
def read_page():

    soap_url = "http://cms-origin.bethel.edu/ws/services/AssetOperationService"
    wsdl_url = 'http://cms-origin.bethel.edu/ws/services/AssetOperationService?wsdl'

    client = Client(url=wsdl_url, location=soap_url)
    return "<pre>" + readPage(client) + "</pre>"


@app.route("/submit", methods=['POST'])
def submit_form():

    ##A dict to populate with all the interesting data.
    add_data = {}

    ##get the form
    form = request.form
    req = request
    ##get the multiselect values
    add_data['general'] = form.getlist('general')
    add_data['academics'] = form.getlist('academics')
    add_data['offices'] = form.getlist('offices')
    add_data['internal'] = form.getlist('internal')

    ##get the normal things
    add_data['featuring'] = form['featuring']
    add_data['location'] = form['location']
    add_data['directions'] = form['directions']
    add_data['sponsors'] = form['sponsors']
    add_data['cost'] = form['cost']
    add_data['details'] = form['details']
    add_data['refunds'] = form['refunds']
    add_data['description'] = form['description']
    add_data['questions'] = form['questions']
    add_data['heading'] = form['heading']

    ##Create a list of dates
    start = form['start1']
    end = form['end1']

    start = start.replace(' GMT-0500 (UTC)', '')
    end = end.replace(' GMT-0500 (UTC)', '')

    start = int(datetime.datetime.strptime(start, '%a %b %d %Y %H:%M:%S').strftime("%s"))
    end = int(datetime.datetime.strptime(end, '%a %b %d %Y %H:%M:%S').strftime("%s"))

    dates = [
        eventDate(start, end, True)
    ]

    ##Add it to the dict
    add_data['dates'] = dates

    resp = create_new_event(add_data)

    ##Just print the response for now
    return resp


def create_new_event(add_data):

    soap_url = "http://cms-origin.bethel.edu/ws/services/AssetOperationService"
    wsdl_url = 'http://cms-origin.bethel.edu/ws/services/AssetOperationService?wsdl'

    client = Client(url=wsdl_url, location=soap_url)

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
        structuredDataNode("off-campus-location", "off-campus-location from Python"),
        structuredDataNode("location", add_data['location']),
        structuredDataNode("featuring", add_data['featuring']),

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
            'name': "test-event",
            'siteId': "ba134ac58c586513100ee2a7cec27f4a",
            'parentFolderPath': "testing",
            'metadataSetPath': "/Event",
            'contentTypePath': "/Event",
            'configurationSetPath': "/Event",
            ## Break this out more once its defined in the form
            'structuredData': structured_data,
            'metadata': {
                'title': "Test",
                'displayName': "Testing",
                'metaDescription': add_data['description'],
                'summary': 'summary',
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


