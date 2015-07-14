# python
import datetime
import time
import arrow

# flask
from flask import session
from flask import abort

# modules
from suds.client import Client
from suds.transport import TransportError

# local
from tinker import app
from tinker import tools


def email_tinker_admins(response):

    if 'success = "false"' in response:
        app.logger.error(session['username'], time.strftime("%c") + " " + str(response))


def delete(page_id, workflow=None):

    client = get_client()

    time.sleep(5.5)

    auth = app.config['CASCADE_LOGIN']

    username = session['username']

    identifier = {
        'id': page_id,
        'type': 'page',
    }

    response = client.service.delete(auth, identifier)
    app.logger.warn(time.strftime("%c") + ": " + page_id + " deleted by " + username + " " + str(response))
    email_tinker_admins(response)
    return response

def get_destinations(destination):
    # empty string means publish to all
    if destination == '':
        return {}
    elif destination == 'staging.bethel.edu':
        id = 'ba1381d58c586513100ee2a78fc41899'
    elif destination == "Production bethel.edu":
        id = '132207cb8c586513742d45fd62673fe4'
    identifier = {'assetIdentifier': {
                    'id': id,
                    'type': 'destination',
                    }
                }
    return identifier


def publish(path_or_id, type='page', destination=""):

    destination = get_destinations(destination)

    client = get_client()

    if path_or_id[0] == "/":
        publishinformation = {
            'identifier': {
                'type': type,
                'path': {
                    'path': path_or_id,
                    'siteId': app.config['SITE_ID']
                }
            },
            'destinations': destination
        }
    else:
        publishinformation = {
            'identifier': {
                'id': path_or_id,
                'type': type,
            },
            'destinations': destination
        }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.publish(auth, publishinformation)
    app.logger.warn(time.strftime("%c") + ": Published " + str(response))

    email_tinker_admins(response)

    return response


def unpublish(page_id, type="page"):

    client = get_client()

    publishinformation = {
        'identifier': {
            'id': page_id,
            'type': type
        },
        'unpublish': True
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.publish(auth, publishinformation)
    app.logger.warn(time.strftime("%c") + ": Unpublished " + str(response))

    email_tinker_admins(response)

    return response


def read_identifier(identifier):
    client = get_client()
    auth = app.config['CASCADE_LOGIN']
    response = client.service.read(auth, identifier)

    email_tinker_admins(response)

    return response


def read(path_or_id, type="page"):
    client = get_client()

    if path_or_id[0] == "/":
        identifier = {
            'type': type,
            'path': {
                'path': path_or_id,
                'siteId': app.config['SITE_ID']
            }
        }
    else:
        identifier = {
            'id': path_or_id,
            'type': type,
        }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.read(auth, identifier)

    email_tinker_admins(response)

    return response


def edit(asset):

    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    response = client.service.edit(auth, asset)

    email_tinker_admins(response)

    return response


def rename(page_id, newname, type="page"):
    """ Rename a page with page_id to have new system-name = newname """
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    identifier = {
        'id': page_id,
        'type': type
    }

    move_parameters = {
        'doWorkflow': False,
        'newName': newname
    }

    response = client.service.move(auth, identifier, move_parameters)
    app.logger.warn(time.strftime("%c") + ": Renamed " + str(response))

    email_tinker_admins(response)

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

    dest_folder_identifier = {
        'path': {
            'siteId': app.config['SITE_ID'],
            'path': destination_path[1],
        },
        'type': 'folder'
    }

    move_parameters = {
        'destinationContainerIdentifier': dest_folder_identifier,
        'doWorkflow': False
    }

    response = client.service.move(auth, identifier, move_parameters)
    app.logger.warn(time.strftime("%c") + ": Moved " + str(response))

    email_tinker_admins(response)

    return response


def date_to_java_unix(date):

    return int(datetime.datetime.strptime(date, '%B %d  %Y, %I:%M %p').strftime("%s")) * 1000


def java_unix_to_date(date, date_format=None):
    if not date_format:
        date_format = "%B %d  %Y, %I:%M %p"
    return datetime.datetime.fromtimestamp(int(date) / 1000).strftime(date_format)


def string_to_datetime(date_str):

    try:
        return datetime.datetime.strptime(date_str, '%B %d  %Y, %I:%M %p').date()
    except TypeError:
        return None


def friendly_date_range(start, end):
    date_format = "%B %d, %Y %I:%M %p"

    start_check = arrow.get(start)
    end_check = arrow.get(end)

    if start_check.year == end_check.year and start_check.month == end_check.month and start_check.day == end_check.day:
        return "%s - %s" % (datetime.datetime.fromtimestamp(int(start)).strftime(date_format), datetime.datetime.fromtimestamp(int(end)).strftime("%I:%M %p"))
    else:
        return "%s - %s" % (datetime.datetime.fromtimestamp(int(start)).strftime(date_format), datetime.datetime.fromtimestamp(int(end)).strftime(date_format))


def read_date_data_dict(node):
    node_data = node['structuredDataNodes']['structuredDataNode']
    date_data = {}
    for date in node_data:
        date_data[date['identifier']] = date['text']
    # If there is no date, these will fail
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
    # If there is no date, these will fail
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

    # publish the event XML page
    publish(app.config['EVENT_XML_ID'])


def publish_faculty_bio_xml():

    # publish the event XML page
    publish(app.config['FACULTY_BIO_XML_ID'])


def publish_e_announcement_xml():

    # publish the event XML page
    publish(app.config['E_ANNOUNCEMENTS_XML_ID'])


def is_asset_in_workflow(id, type="page"):

    tools.get_user()
    client = get_client()
    identifier = {
        'id': id,
        'type': type,
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.readWorkflowInformation(auth, identifier)

    if response.workflow is not None:
        if str(response.workflow.currentStep) != "finish":
            return True

    return False

def search(name_search="", content_search="", metadata_search=""):
    client = get_client()

    search_information = {
        'matchType': "match-all",
        'assetName': name_search,
        'assetContent': content_search,
        'assetMetadata': metadata_search,
        'searchPages': True,
        'searchBlocks': True,
        'searchFiles': True,
        'searchFolders': True,
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.search(auth, search_information)
    # app.logger.warn(time.strftime("%c") + ": Search " + str(response))

    return response


def create_image(asset):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    username = session['username']

    response = client.service.create(auth, asset)
    app.logger.warn(time.strftime("%c") + ": Create image submission by " + username + " " + str(response))

    # Publish
    publish(response.createdAssetId, "file")

    return response


def list_relationships(id, type="page"):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    identifier = {
        'id': id,
        'type': type,
    }

    response = client.service.listSubscribers(auth, identifier)

    return response


def read_access_rights(id, type="page"):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    identifier = {
        'id': id,
        'type': type,
    }

    response = client.service.readAccessRights(auth, identifier)

    return response