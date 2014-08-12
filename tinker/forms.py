# coding: utf-8

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
from wtforms.validators import Optional

#local
from tinker import app
##from tinker import cache
from tinker.web_services import get_client, read


def get_md(metadata_path):

    auth = app.config['CASCADE_LOGIN']

    identifier = {
        'path': {
            'path': metadata_path,
            'siteName': 'Public'
        },
        'type': 'metadataset',
    }

    client = get_client()
    md = client.service.read(auth, identifier)
    return md.asset.metadataSet.dynamicMetadataFieldDefinitions.dynamicMetadataFieldDefinition


#Cache for one day
##@cache.cached(timeout=86400, key_prefix='get_event_choices')
def get_event_choices():

    data = get_md("/Event")

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
    labels.append(("none", '-select-'))
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

    choices = get_event_choices()
    general_choices = choices['general']
    offices_choices = choices['offices']
    academic_dates_choices = choices['academics_dates']
    internal_choices = choices['internal']
    cas_departments_choices = choices['cas_departments']
    building_choices = choices['buildings']

    location_choices = (('', "-select-"), ('On Campus', 'On Campus'), ('Off Campus', 'Off Campus'))
    heading_choices = (('', '-select-'), ('Registration', 'Registration'), ('Ticketing', 'Ticketing'))


    what = HeadingField(label="What is your event?")
    title = TextField('Event Name', validators=[Required()], description="This will be the title of your webpage")
    teaser = TextField('Teaser', description=u'Short (1 sentence) description. What will the attendees expect? This will appear in event viewers and on the calendar.')
    featuring = TextField('Featuring')
    sponsors = TextAreaField('Sponsors')
    main_content = CKEditorTextAreaField('Event description')

    when = HeadingField(label="When is your event?")
    start = DateTimeField("", default=datetime.datetime.now)

    where = HeadingField(label="Where is your event?")
    location = SelectField('Location', choices=location_choices)
    on_campus_location = SelectField('On campus location', choices=building_choices)
    other_on_campus = TextField('Other on campus location')
    off_campus_location = TextField("Off Campus Location")
    maps_directions = CKEditorTextAreaField('Directions', description=u"Information or links to directions and parking information (if applicable). (ex: Get directions to Bethel University. Please park in the Seminary student and visitor lot.)")

    why = HeadingField(label="Does your event require registration or payment?")
    registration_heading = SelectField('Select a heading for the registration section', choices=heading_choices)
    registration_details = CKEditorTextAreaField('Registration/ticketing details', description=u"How do attendees get tickets? Is it by phone, through Bethel’s site, or through an external site? When is the deadline?")
    wufoo_code = TextField('Approved Wufoo Hash Code')
    cost = TextAreaField('Cost')
    cancellations = TextAreaField('Cancellations and refunds')

    other = HeadingField(label="Who should folks contact with questions?")
    questions = CKEditorTextAreaField('Questions', description=u"Contact info for questions. (ex: Contact the Office of Church Relations at 651.638.6301 or church-relations@bethel.edu.)")

    categories = HeadingField(label="Categories")

    general = SelectMultipleField('General Categories', choices=general_choices, validators=[Required()])
    offices = SelectMultipleField('Offices', choices=offices_choices, validators=[Required()])
    academic_dates = SelectMultipleField('Academic Dates', choices=academic_dates_choices, validators=[Required()])
    cas_departments = SelectMultipleField('CAS Academic Department', choices=cas_departments_choices, validators=[Required()])
    internal = SelectMultipleField('Internal Only', choices=internal_choices, validators=[Required()])



#####################
##Faculty Bio Forms
#####################

##Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
##aside from be a marker label
class DummyField(TextAreaField):
    pass

#Cache for one day
##@cache.cached(timeout=86400, key_prefix='get_faculty_bio_choices')
def get_faculty_bio_choices():

    data = get_md("/Robust")

    school_list = data[4].possibleValues.possibleValue
    department_list = data[7].possibleValues.possibleValue

    school = []
    for item in school_list:
        school.append((item.value, item.value))

    department = []
    for item in department_list:
        department.append((item.value, item.value))

    return {'school': school, 'department': department}

class FacultyBioForm(Form):

    title = TextField('Faculty Bio Name', validators=[Required()], description="This will be the title of your webpage")

    job_titles = TextField('')
    email = TextField('Email', validators=[Required()], description="Enter your email")
    started_at_bethel = TextField('Started at Bethel in', validators=[Required()])

    heading_choices = (('', "-select-"), ('Areas of expertise', 'Areas of expertise'), ('Research interests', 'Research interests'), ('Teaching speciality', 'Teaching speciality'))

    heading = SelectField('Choose a heading that best fits your discipline', choices=heading_choices)
    areas = TextField('Areas of expertise')
    research_interests = TextField('Research interests')
    teaching_specialty = TextField('Teaching speciality')

    degree = DummyField('')

    biography = CKEditorTextAreaField('Biography')
    awards = CKEditorTextAreaField('Awards')
    publications = CKEditorTextAreaField('Publications')
    certificates = CKEditorTextAreaField('Certificates and Licenses')
    hobbies = CKEditorTextAreaField('Hobbies and Interests')

    quote = TextField('Quote')

    website = TextField('Professional Website or Blog')



    categories = HeadingField(label="Categories ( Which categories do we want? )")
    choices = get_faculty_bio_choices()
    school_choices = choices['school']
    department_choices = choices['department']

    school = SelectMultipleField('School', choices=school_choices, validators=[Required()])
    department = SelectMultipleField('Undergraduate Departments', choices=department_choices, validators=[Required()])