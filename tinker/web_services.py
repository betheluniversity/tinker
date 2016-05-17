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


# todo don't need anymore because of sentry
def email_tinker_admins(response):

    if 'success = "false"' in response:
        app.logger.error(session['username'], time.strftime("%c") + " " + str(response))

# todo why do we need this?
def get_destinations(destination):
    if destination == 'staging.bethel.edu' or destination == 'staging':
        id = 'ba1381d58c586513100ee2a78fc41899'
        identifier = {'assetIdentifier': {
                    'id': id,
                    'type': 'destination',
                    }
                }
        return identifier
    else:
        return ''


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


# todo what?
def friendly_date_range(start, end):
    date_format = "%B %d, %Y %I:%M %p"

    start_check = arrow.get(start)
    end_check = arrow.get(end)

    if start_check.year == end_check.year and start_check.month == end_check.month and start_check.day == end_check.day:
        return "%s - %s" % (datetime.datetime.fromtimestamp(int(start)).strftime(date_format), datetime.datetime.fromtimestamp(int(end)).strftime("%I:%M %p"))
    else:
        return "%s - %s" % (datetime.datetime.fromtimestamp(int(start)).strftime(date_format), datetime.datetime.fromtimestamp(int(end)).strftime(date_format))


# todo why? Move this to base?
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

# todo why? Move this to base?
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


# todo move
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
    # app.logger.debug(time.strftime("%c") + ": Search " + str(response))

    return response

# todo move
def search_data_definitions(name_search=""):
    client = get_client()

    search_information = {
        'matchType': "match-all",
        'assetName': name_search,
        'searchBlocks': True,
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.search(auth, search_information)

    return response

# todo move
def create_image(asset):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    username = session['username']

    response = client.service.create(auth, asset)
    app.logger.debug(time.strftime("%c") + ": Create image submission by " + username + " " + str(response))

    # Publish
    publish(response.createdAssetId, "file")

    return response

# todo move
def list_relationships(id, type="page"):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    identifier = {
        'id': id,
        'type': type,
    }

    response = client.service.listSubscribers(auth, identifier)

    return response

# todo move
def read_access_rights(id, type="page"):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    identifier = {
        'id': id,
        'type': type,
    }

    response = client.service.readAccessRights(auth, identifier)

    return response