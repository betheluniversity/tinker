#modules
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms import HiddenField
from wtforms import TextAreaField
from wtforms import SelectMultipleField
from wtforms import SelectField
from wtforms import RadioField
from wtforms import DateTimeField
from wtforms.validators import DataRequired
from suds.client import Client

#python
import datetime

#local
from cascade_web_services import app


def read_metadata():

    soap_url = "http://cms-origin.bethel.edu/ws/services/AssetOperationService"
    wsdl_url = 'http://cms-origin.bethel.edu/ws/services/AssetOperationService?wsdl'

    auth = app.config['CASCADE_LOGIN']

    identifier = {
        'path': {
            'path': '/Event',
            'siteName': 'Public'
        },
        'type': 'metadataset',
    }

    client = Client(url=wsdl_url, location=soap_url)
    response = client.service.read(auth, identifier)

    return response


def get_md():

    md = read_metadata()
    data = md.asset.metadataSet.dynamicMetadataFieldDefinitions.dynamicMetadataFieldDefinition

    return data


def get_choices():

    data = get_md()

    general_list = data[0].possibleValues.possibleValue
    offices_list = data[1].possibleValues.possibleValue
    academics_list = data[2].possibleValues.possibleValue
    internal_list = data[3].possibleValues.possibleValue


    general = []
    for item in general_list:
        general.append((item.value, item.value))

    offices = []
    for item in offices_list:
        offices.append((item.value, item.value))

    academics = []
    for item in academics_list:
        academics.append((item.value, item.value))

    internal = []
    for item in internal_list:
        internal.append((item.value, item.value))

    return {'general': general, 'offices': offices, 'academics': academics, 'internal': internal}

#class StartEndDateField()

class EventForm(Form):

    choices = get_choices()
    general_choices = choices['general']
    offices_choices = choices['offices']
    academics_choices = choices['academics']
    internal_choices = choices['internal']

    location_choices = (('On Campus', 'On Campus'), ('Off Campus', 'Off Campus'))
    heading_choices = (('Registration', 'Registration'), ('Ticketing', 'Ticketing'))

    featuring = TextField('Featuring')
    location = SelectField('Location', choices=location_choices)
    off_location = TextField("Off Campus Location")
    directions = TextAreaField('Directions')
    sponsors = TextAreaField('Sponsors')
    cost = TextAreaField('Cost')
    heading = RadioField('Heading', choices=heading_choices)
    details = TextAreaField('Registration/ticketing details')
    refunds = TextAreaField('Cancellations and refunds')
    description = TextAreaField('Event description')
    questions = TextAreaField('Questions')

    start = DateTimeField("Start Date", default=datetime.datetime.now)
    general = SelectMultipleField('General Categories', choices=general_choices)
    offices = SelectMultipleField('Offices', choices=offices_choices)
    academics = SelectMultipleField('Academics', choices=academics_choices)
    internal = SelectMultipleField('Internal Only', choices=internal_choices)


