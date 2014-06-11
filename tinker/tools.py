#python
from datetime import date

#modules
from suds.client import Client
from flask import request

#local
from tinker import app


def get_client():

    return Client(url=app.config['WSDL_URL'], location=app.config['SOAP_URL'])


def get_user():

    if app.config['ENVIRON'] == 'prod':
        user = request.environ.get('REMOTE_USER')
    else:
        user = app.config['TEST_USER']

    return user


def get_folder_path(data):
    #Check to see if this event should go in a specific folder

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
