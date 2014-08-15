# coding: utf-8

#python

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
