from flask.ext.wtf import Form
from flask_wtf.file import FileField
from tinker import app
import requests
from tinker.faculty_bios.faculty_bio_controller import *
from wtforms import Field
from wtforms import HiddenField
from wtforms import SelectField
from wtforms import TextAreaField
from wtforms import TextField
from wtforms import ValidationError
from wtforms import validators

tinker = TinkerController

def get_md(metadata_path):
    md = tinker.read(metadata_path, type='metadataset')
    return md['asset']['metadataSetdynamic']['MetadataFieldDefinitionsdynamic']['MetadataFieldDefinition']


# Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
# aside from be a marker label
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


#####################
# #Faculty Bio Forms
#####################

# Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
# aside from be a marker label
class DummyField(TextAreaField):
    pass


def validate_username(form, field):
    username = field.data
    host = "http://wsapi.bethel.edu"
    path = "/username/" + username + "/roles"
    req = requests.get(host + path)

    content = req.content
    if content == str({}):
        raise ValidationError("Enter the username you use to login to Blink and don't include '@bethel.edu'.")


class FacultyBioForm(Form):
    roles = session['roles']

    # if a cas faculty member or seminary faculty member, hide the image field.
    if 'Tinker Faculty Bios' in session['groups']:
        image = FileField("Image")
        image_url = HiddenField("Image URL")
    elif 'FACULTY-CAS' in roles or 'FACULTY-BSSP' in roles or 'FACULTY-BSSD' in roles:
        image = HiddenField("Image")
        image_url = HiddenField("Image URL")
    else:
        image = FileField("Image")
        image_url = HiddenField("Image URL")

    first = TextField('Faculty first name', validators=[validators.DataRequired()])
    last = TextField('Faculty last name', validators=[validators.DataRequired()])
    author = TextField("Faculty member's username", validators=[validators.DataRequired(), validate_username],
                       description="Enter your Bethel username.")

    new_job_titles = TextField('')

    email = TextField('Email', validators=[validators.DataRequired()])
    started_at_bethel = TextField('Started at Bethel in', validators=[validators.DataRequired()],
                                  description="Enter a year")

    heading_choices = (
        ('', "-select-"), ('Areas of expertise', 'Areas of expertise'), ('Research interests', 'Research interests'),
        ('Teaching Specialty', 'Teaching Specialty'))

    heading = SelectField('Choose a heading that best fits your discipline', choices=heading_choices,
                          validators=[validators.DataRequired()])
    areas = TextAreaField('Areas of expertise', description="A max of 3000 characters is permitted. Current count: ",
                          validators=[validators.length(max=3000,
                                                        message="Character limit exceeded. A max of 3000 characters is allowed.")])
    research_interests = TextAreaField('Research interests',
                                       description="A max of 3000 characters is permitted. Current count: ",
                                       validators=[validators.length(max=3000,
                                                                     message="Character limit exceeded. A max of 3000 characters is allowed.")])
    teaching_specialty = TextAreaField('Teaching specialty',
                                       description="A max of 3000 characters is permitted. Current count: ",
                                       validators=[validators.length(max=3000,
                                                                     message="Character limit exceeded. A max of 3000 characters is allowed.")])

    degree = DummyField('')

    biography = CKEditorTextAreaField('Biography')
    courses = CKEditorTextAreaField('Courses Taught')
    awards = CKEditorTextAreaField('Awards')
    publications = CKEditorTextAreaField('Publications')
    presentations = CKEditorTextAreaField('Presentations')
    certificates = CKEditorTextAreaField('Certificates and licenses')
    organizations = CKEditorTextAreaField('Professional Organizations, Committees, and Boards')
    hobbies = CKEditorTextAreaField('Hobbies and interests')

    quote = TextField('Quote')

    website = TextField('Professional website or blog')

    # Manually override validate, in order to check the 3 headers below
    def validate(self):
        if not Form.validate(self):
            for field, errors in self.errors.items():
                print field, errors
            return False
        result = True

        if self.heading.data == "Areas of expertise":
            if self.areas.data == "":
                self.areas.errors.append('Area of expertise is required.')
                result = False
        elif self.heading.data == "Research interests":
            if self.research_interests.data == "":
                self.research_interests.errors.append('Research interests is required.')
                result = False
        elif self.heading.data == "Teaching speciality":
            if self.teaching_specialty.data == "":
                self.teaching_specialty.errors.append('Teaching speciality is required.')
                result = False

        return result
