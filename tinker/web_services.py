#python
import datetime
import time
import requests

#flask
from flask import request
from flask import session
from flask import json as fjson

#modules
from suds.client import Client

#local
from tinker import app, cache


def delete(page_id):

    client = get_client()

    identifier = {
        'id': page_id,
        'type': 'page',
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.delete(auth, identifier)
    app.logger.warn(time.strftime("%c") + ": Deleted " + str(response))
    ## Publish the XML so the event is gone
    publish_event_xml()
    return response


def publish(page_id):

    client = get_client()

    publishinformation = {
        'identifier': {
            'id': page_id,
            'type': 'page'
        }
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.publish(auth, publishinformation)
    app.logger.warn(time.strftime("%c") + ": Published " + str(response))

    return response


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
    app.logger.warn(time.strftime("%c") + ": Edit " + str(response))
    ##publish the xml file so the new event shows up
    publish_event_xml()

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
    app.logger.warn(time.strftime("%c") + ": Moved " + str(response))
    ##publish the xml file so the new event shows up
    publish_event_xml()

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
        username = request.environ.get('REMOTE_USER')
    else:
        username = app.config['TEST_USER']
        session['username'] = username
        get_roles(username)
    return username


def get_roles(username):

    url = app.config['API_URL'] + "/username/%s/roles" % username
    r = requests.get(url, auth=(app.config['API_USERNAME'], app.config['API_PASSWORD']))
    roles = fjson.loads(r.content)
    ret = []
    for key in roles.keys():
        ret.append(roles[key]['userRole'])

    if username == 'ejc84332':
        ret.append('FACULTY')

    session['roles'] = ret

    return ret


def get_client():

    return Client(url=app.config['WSDL_URL'], location=app.config['SOAP_URL'])


def publish_event_xml():

    #publish the event XML page
    publish(app.config['EVENT_XML_ID'])

    #clear Flask-Cache

    with app.app_context():
        cache.clear()