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
from wtforms import FieldList
from wtforms import FormField
from wtforms import Field
from wtforms import Label
from wtforms.validators import Required

#local
from tinker import app
from tinker.web_services import get_client, read


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
    academic_dates_list = data[2].possibleValues.possibleValue
    cas_departments_list = data[3].possibleValues.possibleValue
    internal_list = data[4].possibleValues.possibleValue

    general = []
    for item in general_list:
        general.append((item.value, item.value))

    offices = []
    for item in offices_list:
        offices.append((item.value, item.value))

    academic_dates = []
    for item in academic_dates_list:
        academic_dates.append((item.value, item.value))

    internal = []
    for item in internal_list:
        internal.append((item.value, item.value))

    cas_departments = []
    for item in cas_departments_list:
        cas_departments.append((item.value, item.value))

    ## Get the building choices from the block
    building_choices = get_buildings()

    return {'general': general, 'offices': offices, 'academics_dates': academic_dates,
            'internal': internal, 'cas_departments': cas_departments, 'buildings': building_choices}


def get_buildings():
    page = read('ba1355ea8c586513100ee2a725b9ebea', type="block")
    buildings = page.asset.xhtmlDataDefinitionBlock.structuredData.structuredDataNodes.structuredDataNode[0].structuredDataNodes.structuredDataNode
    labels = []
    labels.append((None, '-select-'))
    for building in buildings:
        label = building.structuredDataNodes.structuredDataNode[0].text
        labels.append((label, label))

    return labels



##Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
##aside from be a marker label
class CKEditorTextAreaField(TextAreaField):
    pass


class HeadingField(Field):

    def __init__(self, label=None, validators=None, filters=tuple(),
                 description='', id=None, default=None, widget=None,
                 _form=None, _name=None, _prefix='', _translations=None):

        self.default = default
        self.description = description
        self.filters = filters
        self.flags = None
        self.name = _prefix + _name
        self.short_name = _name
        self.type = type(self).__name__
        self.validators = validators or list(self.validators)

        self.id = id or self.name
        self.label = label

    def __unicode__(self):
        return None

    def __str__(self):
        return None

    def __html__(self):
        return None


class EventForm(Form):

    choices = get_choices()
    general_choices = choices['general']
    offices_choices = choices['offices']
    academic_dates_choices = choices['academics_dates']
    internal_choices = choices['internal']
    cas_departments_choices = choices['cas_departments']
    building_choices = choices['buildings']

    location_choices = (('On Campus', 'On Campus'), ('Off Campus', 'Off Campus'))
    heading_choices = (('Registration', 'Registration'), ('Ticketing', 'Ticketing'))


    what = HeadingField(label="What is your event?")
    title = TextField('Event Name', validators=[Required()])
    teaser = TextField('Teaser', validators=[Required()])
    featuring = TextField('Featuring', validators=[Required()])
    sponsors = TextAreaField('Sponsors')
    main_content = CKEditorTextAreaField('Event description', validators=[Required()])

    when = HeadingField(label="When is your event?")
    start = DateTimeField("Start Date", default=datetime.datetime.now)

    where = HeadingField(label="Where is your event?")
    location = SelectField('Location', choices=location_choices, validators=[Required()])
    on_campus_location = SelectField('On campus location', choices=building_choices)
    other_on_campus = TextField('Other on campus location')
    off_campus_location = TextField("Off Campus Location")
    maps_directions = CKEditorTextAreaField('Directions')

    why = HeadingField(label="Does your event require registration or payment?")
    registration_heading = RadioField('Heading', choices=heading_choices)
    registration_details = CKEditorTextAreaField('Registration/ticketing details', validators=[Required()])
    wufoo_code = TextField('Approved Wufoo Hash Code')
    cost = TextAreaField('Cost')
    cancellations = TextAreaField('Cancellations and refunds')

    other = HeadingField(label="Who should folks contact with questions?")
    questions = CKEditorTextAreaField('Questions', validators=[Required()])

    categories = HeadingField(label="Categories")

    general = SelectMultipleField('General Categories', choices=general_choices, validators=[Required()])
    offices = SelectMultipleField('Offices', choices=offices_choices, validators=[Required()])
    academic_dates = SelectMultipleField('Academic Dates', choices=academic_dates_choices, validators=[Required()])
    cas_departments = SelectMultipleField('CAS Academic Department', choices=cas_departments_choices, validators=[Required()])
    internal = SelectMultipleField('Internal Only', choices=internal_choices, validators=[Required()])


