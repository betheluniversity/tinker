#python
import datetime
import time
import arrow

#flask
from flask import session
from flask import abort

#modules
from suds.client import Client
from suds.transport import TransportError

#local
from tinker import app


def delete(page_id, workflow=None):

    client = get_client()

    identifier = {
        'id': page_id,
        'type': 'page',
    }

    auth = app.config['CASCADE_LOGIN']

    stat = unpublish(page_id)

    #dirty. Fix later
    time.sleep(5.5)

    username = session['username']

    response = client.service.delete(auth, identifier)
    app.logger.warn(time.strftime("%c") + ": Deleted by " + username + " " + str(response))

    ## Publish the XMLs
    publish_event_xml()
    publish_faculty_bio_xml()

    return response


def publish(page_id, type='page'):

    client = get_client()

    publishinformation = {
        'identifier': {
            'id': page_id,
            'type': type,

        },
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.publish(auth, publishinformation)
    app.logger.warn(time.strftime("%c") + ": Published " + str(response))

    return response


def unpublish(page_id):

    client = get_client()

    publishinformation = {
        'identifier': {
            'id': page_id,
            'type': 'page'
        },
        'unpublish': True
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.publish(auth, publishinformation)
    app.logger.warn(time.strftime("%c") + ": Unpublished " + str(response))

    return response


def read_identifier(identifier):
    client = get_client()
    auth = app.config['CASCADE_LOGIN']
    response = client.service.read(auth, identifier)
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

    return response


def rename(page_id, newname):
    """ Rename a page with page_id to have new system-name = newname """
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    identifier = {
        'id': page_id,
        'type': 'page'
    }

    moveParameters =  {
        'doWorkflow': False,
        'newName': newname
    }

    response = client.service.move(auth, identifier, moveParameters)
    app.logger.warn(time.strftime("%c") + ": Renamed " + str(response))
    ##publish the xml file so the new event shows up
    return response


def move(page_id, destination_path):
    """ Move a page with page_id to folder with path destination_path """
    app.logger.warn(time.strftime("%c") + ": Moved " + str(destination_path))
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    identifier = {
        'id': page_id,
        'type': 'page'
    }

    destFolderIdentifier = {
        'path': {
            'siteId': app.config['SITE_ID'],
            'path': destination_path[1],
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


    return response


def date_to_java_unix(date):

    return int(datetime.datetime.strptime(date, '%B %d  %Y, %I:%M %p').strftime("%s")) * 1000


def java_unix_to_date(date, format=None):
    if not format:
        format = "%B %d  %Y, %I:%M %p"
    return datetime.datetime.fromtimestamp(int(date) / 1000).strftime(format)


def string_to_datetime(date_str):

    try:
        return datetime.datetime.strptime(date_str, '%B %d  %Y, %I:%M %p').date()
    except TypeError:
        return None


def friendly_date_range(start, end):
    start = arrow.get(start)
    end = arrow.get(end)
    if start.year == end.year and start.month == end.month and start.day == end.day:
        return "%s - %s" % (start.format('MMM d, YYYY h:mm a'), end.format('h:mm a'))
    else:
        return "%s - %s" % (start.format('MMM d, YYYY h:mm a'), end.format('MMM d, YYYY h:mm a'))


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


def get_client():
    try:
        client = Client(url=app.config['WSDL_URL'], location=app.config['SOAP_URL'])
        return client
    except TransportError:
        abort(503)


def publish_event_xml():

    #publish the event XML page
    publish(app.config['EVENT_XML_ID'])

    #clear Flask-Cache

    ##with app.app_context():
    ##    cache.clear()


def publish_faculty_bio_xml():

    #publish the event XML page
    publish(app.config['FACULTY_BIO_XML_ID'])

    #clear Flask-Cache

    ##with app.app_context():
    ##    cache.clear()
