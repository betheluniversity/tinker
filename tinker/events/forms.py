# coding: utf-8
# Global
from datetime import datetime

# Packages
from bu_cascade.asset_tools import find, convert_asset
from flask import session
from flask_wtf import FlaskForm
from wtforms import DateTimeField, HiddenField, SelectField, SelectMultipleField, StringField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, InputRequired

# Local
from tinker.tinker_controller import TinkerController

tinker = TinkerController()


def get_md(metadata_path):
    md = tinker.read(metadata_path, 'metadataset')
    return md['asset']['metadataSet']['dynamicMetadataFieldDefinitions']['dynamicMetadataFieldDefinition']

def get_event_choices():
    data = get_md("/Event")

    md = {}
    for item in data:
        try:
            md[item['name']] = item['possibleValues']['possibleValue']
        except:
            continue

    md = convert_asset(md)

    general = []
    for item in md['general']:
        general.append((item['value'], item['value']))

    offices = []
    for item in md['offices']:
        offices.append((item['value'], item['value']))

    internal = []
    for item in md['internal']:
        internal.append((item['value'], item['value']))

    cas_departments = []
    for item in md['cas-departments']:
        cas_departments.append((item['value'], item['value']))

    adult_undergrad_program = []
    for item in md['adult-undergrad-program']:
        adult_undergrad_program.append((item['value'], item['value']))

    graduate_program = []
    for item in md['graduate-program']:
        graduate_program.append((item['value'], item['value']))

    seminary_program = []
    for item in md['seminary-program']:
        seminary_program.append((item['value'], item['value']))

    # Get the building choices from the block
    building_choices = get_buildings()

    return {'general': general,
            'offices': offices,
            'internal': internal,
            'cas_departments': cas_departments,
            'adult_undergrad_program': adult_undergrad_program,
            'graduate_program': graduate_program,
            'seminary_program': seminary_program,
            'buildings': building_choices
            }


def get_buildings():
    labels = [("none", '-select-')]
    block = convert_asset(tinker.read('04d538728c5865132abe9a84a6e0838d', type="block"))
    buildings = find(block, 'buildings')
    for building in buildings:
        label = building['structuredDataNodes']['structuredDataNode'][0]['text']
        labels.append((label, label))

    return labels


# Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
# aside from be a marker label
class CKEditorTextAreaField(TextAreaField):
    pass

# Long words throw off formatting in Calendar
def length_checker(Form, field):
    word_split = field.data.split(" ")
    for word in word_split:
        if len(word) > 15:
            raise ValidationError('Words in the title must be 15 characters or less')
        
# Custom validator to ensure the cost is numeric
def validate_numeric(form, field):
    try:
        float(field.data)  # Check if the value can be converted to a float
    except ValueError:
        raise ValidationError("Cost must be a numeric value.")
    
class EventForm(FlaskForm):
    image = HiddenField("Image path")

    choices = get_event_choices()
    general_choices = choices['general']
    offices_choices = choices['offices']
    internal_choices = choices['internal']
    cas_departments_choices = choices['cas_departments']
    adult_undergrad_program_choices = choices['adult_undergrad_program']
    graduate_program = choices['graduate_program']
    seminary_program_choices = choices['seminary_program']
    building_choices = choices['buildings']

    location_choices = (('On Campus', 'On Campus'), ('Other On Campus', 'Other On Campus'), ('Off Campus', 'Off Campus'), ('Online', 'Online'))
    heading_choices = (('', '-select-'), ('Registration', 'Registration'), ('Ticketing', 'Ticketing'))

    what = StringField('label', description="What is your event?")
    title = StringField('Event name', validators=[DataRequired() , length_checker], description="This will be the title of your webpage")

    metaDescription = StringField('Teaser',
                                  description=u'Short (1 sentence) description. What will the attendees expect? This will appear in event viewers and on the calendar.',
                                  validators=[DataRequired()])

    if 'Event Approver' in session['groups']:
        link = StringField("External Link",
                           description="This field only seen by 'Event Approvers'. An external link will redirect this event to the external link url.")
    else:
        link = HiddenField("External Link")

    featuring = StringField('Featuring')
    sponsors = CKEditorTextAreaField('Sponsors')
    main_content = CKEditorTextAreaField('Event description')

    when = StringField('label', description="When is your event?")
    start = DateTimeField("", default=datetime.now)

    where = StringField('label', description="Where is your event?")

    location = SelectField('Location', choices=location_choices)
    online_url = StringField('Online URL', description="Enter full URL including 'https://'")
    on_campus_location = SelectField('On campus location', choices=building_choices)
    other_on_campus = StringField('Other on campus location')
    off_campus_name = StringField('Location Name', description="Name of the off campus location")
    off_campus_address = StringField('Street Address', description="Street Address of the off campus location")
    off_campus_city = StringField('City', description="City of the off campus location")
    off_campus_state = StringField('State', description="State of the off campus location. Use two-letter state code (ex. MN)")
    off_campus_zip = StringField('Zip Code', description="Zip Code of the off campus location")

    maps_directions = CKEditorTextAreaField('Instructions for Guests',
                                            description=u"Information or links to directions and parking information (if applicable). (ex: Get directions to Bethel University. Please park in the Seminary student and visitor lot.)")

    why = StringField('label', description="Does your event require registration or payment?")
    registration_heading = SelectField('Select a heading for the registration section', choices=heading_choices)
    registration_details = CKEditorTextAreaField('Registration/ticketing details',
                                                 description=u"How do attendees get tickets? Is it by phone, through Bethel’s site, or through an external site? When is the deadline?")
    wufoo_code = StringField('Approved wufoo hash code')
    ticketing_url = StringField('Ticketing URL')
    cost = StringField('Cost', description="Please enter a number. If the event is Free, enter 0.", validators=[InputRequired(message="Cost is required."), validate_numeric])
    cancellations = TextAreaField('Cancellations and refunds')

    other = StringField('label', description="Who should folks contact with questions?")
    questions = CKEditorTextAreaField('Questions',
                                      description=u"Contact info for questions. (ex: Contact the Office of Church Relations at 651.638.6301 or church-relations@bethel.edu.)",
                                  validators=[DataRequired()])

    categories = StringField('label', description="Categories")

    general = SelectMultipleField('General categories', choices=general_choices, default=['None'],
                                  validators=[DataRequired()])
    offices = SelectMultipleField('Offices', choices=offices_choices, default=['None'], validators=[DataRequired()])
    cas_departments = SelectMultipleField('CAS academic department', default=['None'], choices=cas_departments_choices,
                                          validators=[DataRequired()])
    adult_undergrad_program = SelectMultipleField('CAPS programs', default=['None'],
                                                  choices=adult_undergrad_program_choices, validators=[DataRequired()])
    seminary_program = SelectMultipleField('Seminary programs', default=['None'], choices=seminary_program_choices,
                                           validators=[DataRequired()])
    graduate_program = SelectMultipleField('GS Programs', default=['None'], choices=graduate_program,
                                           validators=[DataRequired()])
    internal = SelectMultipleField('Internal only', default=['None'], choices=internal_choices,
                                   validators=[DataRequired()])