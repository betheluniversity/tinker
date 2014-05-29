#python

#modules
from suds.client import Client

#local
from cascade_web_services import app


def get_client():

    return Client(url=app.config['WSDL_URL'], location=app.config['SOAP_URL'])