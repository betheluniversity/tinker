#python
from datetime import date

#modules
from suds.client import Client
from flask import request

#local
from tinker import app
from cascade_events import java_unix_to_date


def get_client():

    return Client(url=app.config['WSDL_URL'], location=app.config['SOAP_URL'])


def get_user():

    if app.config['ENVIRON'] == 'prod':
        user = request.environ.get('REMOTE_USER')
    else:
        user = app.config['TEST_USER']

    return user


def read_date_from_structureddata(node):
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


def get_folder_path(data):
    #Check to see if this event should go in a specific folder

    #Find the year we want
    dates = data['dates']
    for node in dates:
        date_data = read_date_from_structureddata(node)
        x = 1

    path = "events/%s" % date.today().year

    academic_dates = data['academic_dates']
    if len(academic_dates) > 1:
        return path + "/academic-dates"

    if len(academic_dates) == 1 and academic_dates[0] != "None":
        return path + "/academic-dates"

    general = data['general']
    if 'Athletics' in general:
        return path + "/athletics"

    offices = data['offices']
    if 'Bethel Student Government' in offices:
        return path + "/bsg"

    if 'Career Development' in offices:
        return path + "/career-development-calling"

    if 'Library' in general:
        return path + "/library"
