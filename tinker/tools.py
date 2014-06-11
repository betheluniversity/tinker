#python

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