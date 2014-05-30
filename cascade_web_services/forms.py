#python
import datetime

#modules
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import SelectMultipleField
from wtforms import SelectField
from wtforms import RadioField
from wtforms import DateTimeField
from wtforms.validators import Required
#local
from cascade_web_services import app
from tools import get_client


def get_md():

    auth = app.config['CASCADE_LOGIN']

    identifier = {
        'path': {
            'path': '/Event',
            'siteName': 'Public'
        },
        'type': 'metadataset',
    }

    client = get_client()
    md = client.service.read(auth, identifier)
    return md.asset.metadataSet.dynamicMetadataFieldDefinitions.dynamicMetadataFieldDefinition


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


##Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
##aside from be a marker label
class CKEditorTextAreaField(TextAreaField):
    pass


class EventForm(Form):

    choices = get_choices()
    general_choices = choices['general']
    offices_choices = choices['offices']
    academics_choices = choices['academics']
    internal_choices = choices['internal']

    location_choices = (('On Campus', 'On Campus'), ('Off Campus', 'Off Campus'))
    heading_choices = (('Registration', 'Registration'), ('Ticketing', 'Ticketing'))

    title = TextField('Title', validators=[Required()])
    featuring = TextField('Featuring', validators=[Required()])
    location = SelectField('Location', choices=location_choices, validators=[Required()])
    off_location = TextField("Off Campus Location")
    directions = CKEditorTextAreaField('Directions')
    sponsors = TextAreaField('Sponsors')
    cost = TextAreaField('Cost')
    heading = RadioField('Heading', choices=heading_choices)
    details = CKEditorTextAreaField('Registration/ticketing details', validators=[Required()])
    refunds = TextAreaField('Cancellations and refunds')
    description = CKEditorTextAreaField('Event description', validators=[Required()])
    questions = CKEditorTextAreaField('Questions', validators=[Required()])
    wufoo = TextField('Approved Wufoo Hash Code')

    start = DateTimeField("Start Date", default=datetime.datetime.now)
    general = SelectMultipleField('General Categories', choices=general_choices, validators=[Required()])
    offices = SelectMultipleField('Offices', choices=offices_choices, validators=[Required()])
    academics = SelectMultipleField('Academics', choices=academics_choices, validators=[Required()])
    internal = SelectMultipleField('Internal Only', choices=internal_choices, validators=[Required()])


