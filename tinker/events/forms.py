# coding: utf-8
# Global
from datetime import datetime

# Packages
from bu_cascade.asset_tools import find, convert_asset
from flask import session
from flask_wtf import FlaskForm
from wtforms import DateTimeField, HiddenField, SelectField, SelectMultipleField, StringField, TextAreaField, BooleanField, Field
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

class FieldsetField(Field):
    """
    Custom field to handle fieldsets.
    """

    def __init__(self, label='', fields=None, required=False, hidden=False, fieldset_type="multiple", validators=None, **kwargs):
        super(FieldsetField, self).__init__(label, validators, **kwargs)
        self.label.text = label
        self.fields = fields() if callable(fields) else (fields or [])
        self.fieldset_type = fieldset_type
        self.required = required
        self.hidden = hidden

def get_date_fields():
    all_day = BooleanField("All Day", default=False, render_kw={"onclick": "checkboxClicked(this)", "value": "Yes"})
    start_date = DateTimeField("Start Date", render_kw={"onchange": "fillEndDate(this)"}, validators=[InputRequired(message="Start date is required.")])
    end_date = DateTimeField("End Date", validators=[InputRequired(message="End date is required.")])
    no_end = BooleanField("No End Date", default=False, render_kw={"onclick": "toggleFieldsetField(this, 'end_date', 'hide'); checkboxClicked(this)", "value": "Yes"})
    outside_of_minnesota = BooleanField("Outside of Minnesota?", default=False, render_kw={"onclick": "toggleFieldsetField(this, 'timezone', 'show'); checkboxClicked(this)", "value": "Yes"})
    timezone_choices = [
        ('Central Time', 'Central Time'),
        ('Eastern Time', 'Eastern Time'),
        ('Mountain Time', 'Mountain Time'),
        ('Pacific Time', 'Pacific Time'),
        ('Alaska Time', 'Alaska Time'),
        ('Hawaii-Aleutian Time', 'Hawaii-Aleutian Time'),
    ]
    date_timezone = SelectField(
        "Timezone",
        choices=timezone_choices,
        default='Central Time',
        render_kw={"class": "timezoneselect visually-hidden"}
    )

    fields = {
        'all_day': all_day,
        'start_date': start_date,
        'end_date': end_date,
        'no_end': no_end,
        'outside_of_minnesota': outside_of_minnesota,
        'timezone': date_timezone
    }
    
    return fields

def get_cost_fields():
    amount = StringField('Cost', description="Please enter a number. If the event is Free, enter 0.", validators=[InputRequired(message="Cost is required."), validate_numeric])
    description = StringField('Description', description="Ex. \"Senior Citizen (65+) and Group of 10 or more\"", validators=[DataRequired()])

    fields = {
        'amount': amount,
        'description': description
    }
    
    return fields

def get_off_campus_location_fields():
    off_campus_name = StringField('Location Name', description="Name of the off campus location")
    off_campus_address = StringField('Street Address', description="Street Address of the off campus location")
    off_campus_city = StringField('City', description="City of the off campus location")
    off_campus_state = StringField('State', description="State of the off campus location. Use two-letter state code (ex. MN)")
    off_campus_zip = StringField('Zip Code', description="Zip Code of the off campus location")

    fields = {
        'off_campus_name': off_campus_name,
        'off_campus_address': off_campus_address,
        'off_campus_city': off_campus_city,
        'off_campus_state': off_campus_state,
        'off_campus_zip': off_campus_zip
    }
    
    return fields

def bind_fields(form, fields, attribute_name):
    for name, field in fields.items():
        bound_field = field.bind(form, name)
        bound_field.data = None
        fields[name] = bound_field

    attribute = getattr(form, attribute_name, None)
    if attribute is not None:
        attribute.fields = list(fields.values())
        setattr(form, attribute_name, attribute)

def get_event_form(**edit_data):
    """
    Returns an instance of the EventForm with the necessary fields.
    This is used to create a new event or edit an existing one.
    """
    if edit_data:
        form = EventForm(**edit_data)
    else:
        form = EventForm()

    for field in form:
        if isinstance(field, FieldsetField):
            # Bind the fields in the fieldset
            bind_fields(form, field.fields, field.name)

    return form
    
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

    what = StringField('heading', description="What is your event?")
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

    when = StringField('heading', description="When is your event?")

    event_dates = FieldsetField(label="Date and Time", fields=get_date_fields)

    where = StringField('heading', description="Where is your event?")

    # The value is set to the field that should be displayed based on the location choice
    # This is used in the template to show/hide the correct fields
    location_choices = location_choices = [
        ('on_campus_location', 'On Campus'),
        ('other_on_campus', 'Other On Campus'),
        ('off_campus_location', 'Off Campus'),
        ('online_url', 'Online'),
    ]
    location_name = SelectField('Location', choices=location_choices, render_kw={"onchange": "selectChanged(this)"})

    # Location fields are shown/hidden based on the location choice
    online_url = StringField('Online URL', description="Enter full URL including 'https://'")
    on_campus_location = SelectField('On campus location', choices=building_choices)
    other_on_campus = StringField('Other on campus location')
    off_campus_location = FieldsetField(label="Off Campus Location", fields=get_off_campus_location_fields, required=True, hidden=True, fieldset_type="single")

    maps_directions = CKEditorTextAreaField('Instructions for Guests',
                                            description=u"Information or links to directions and parking information (if applicable). (ex: Get directions to Bethel University. Please park in the Seminary student and visitor lot.)")

    # Registration and Ticketing fields
    why = StringField('heading', description="Does your event require registration or payment?")
    heading_choices = [
        ('', '-select-'),
        ('wufoo_code', 'Registration'),
        ('ticketing_url', 'Ticketing')
    ]
    registration_heading = SelectField('Select a heading for the registration section', choices=heading_choices, render_kw={"onchange": "selectChanged(this)"})
    wufoo_code = StringField('Approved wufoo hash code')
    ticketing_url = StringField('Ticketing URL')
    registration_details = CKEditorTextAreaField('Registration/ticketing details',
                                                 description=u"How do attendees get tickets? Is it by phone, through Bethel’s site, or through an external site? When is the deadline?")

    pricing = StringField('heading', description="What is the cost for your event?")
    cost = FieldsetField(label="Event Cost", fields=get_cost_fields)

    cancellations = TextAreaField('Cancellations and refunds')

    other = StringField('heading', description="Who should folks contact with questions?")
    questions = CKEditorTextAreaField('Questions',
                                      description=u"Contact info for questions. (ex: Contact the Office of Church Relations at 651.638.6301 or church-relations@bethel.edu.)",
                                  validators=[DataRequired()])

    categories = StringField('heading', description="Categories")

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