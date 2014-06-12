#python
import datetime
#flask
from flask import request

#modules
from suds.client import Client

#local
from tinker import app


def delete(page_id):

    client = get_client()

    identifier = {
        'id': page_id,
        'type': 'page',
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.delete(auth, identifier)
    ## Publish the XML so the event is gone
    publish(app.config['EVENT_XML_ID'])
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


def publish(id):

    client = get_client()

    publishinformation = {
        'identifier': {
            'id': id,
            'type': 'page'
        }
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.publish(auth, publishinformation)

    return str(response)


def read(read_id, type="page"):

    client = get_client()

    identifier = {
        'id': read_id,
        'type': type
    }


    auth = app.config['CASCADE_LOGIN']

    response = client.service.read(auth, identifier)

    return response


def edit(asset):

    auth = app.config['CASCADE_LOGIN']
    client = get_client()
    response = client.service.edit(auth, asset)

    ##publish the xml file so the new event shows up
    publish(app.config['EVENT_XML_ID'])

    return response


def move(page_id, destination_path):
    """ Move a page with page_id to folder with path destination_path """

    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    identifier = {
        'id': page_id,
        'type': 'page'
    }

    destFolderIdentifier = {
        'path': {
            'path': destination_path,
            'siteId': app.config['SITE_ID']
        },
        'type': 'folder'
    }

    moveParameters =  {
        'destinationContainerIdentifier': destFolderIdentifier,
        'doWorkflow': False
    }

    response = client.service.move(auth, identifier, moveParameters)

    ##publish the xml file so the new event shows up
    publish(app.config['EVENT_XML_ID'])

    return response


def date_to_java_unix(date):

    return int(datetime.datetime.strptime(date, '%B %d  %Y, %I:%M %p').strftime("%s")) * 1000


def java_unix_to_date(date):

    return datetime.datetime.fromtimestamp(int(date) / 1000).strftime('%B %d  %Y, %I:%M %p')


def string_to_datetime(date_str):

    try:
        return datetime.datetime.strptime(date_str, '%B %d  %Y, %I:%M %p').date()
    except TypeError:
        return None


def read_date_data_dict(node):
    node_data = node['structuredDataNodes']['structuredDataNode']
    date_data = {}
    for date in node_data:
        date_data[date['identifier']] = date['text']
    ##If there is no date, these will fail
    try:
        date_data['start-date'] = java_unix_to_date(date_data['start-date'])
    except TypeError:
        pass
    try:
        date_data['end-date'] = java_unix_to_date(date_data['end-date'])
    except TypeError:
        pass

    return date_data


def read_date_data_structure(node):
    node_data = node.structuredDataNodes.structuredDataNode
    date_data = {}
    for date in node_data:
        date_data[date.identifier] = date.text
    ##If there is no date, these will fail
    try:
        date_data['start-date'] = java_unix_to_date(date_data['start-date'])
    except TypeError:
        pass
    try:
        date_data['end-date'] = java_unix_to_date(date_data['end-date'])
    except TypeError:
        pass

    return date_data


def get_user():

    if app.config['ENVIRON'] == 'prod':
        user = request.environ.get('REMOTE_USER')
    else:
        user = app.config['TEST_USER']

    return user


def get_client():

    return Client(url=app.config['WSDL_URL'], location=app.config['SOAP_URL'])